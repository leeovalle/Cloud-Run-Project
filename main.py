import os
import sys
import traceback
import json
#final
import google.generativeai as genai
from flask import Flask, redirect, request, send_file

from storage import upload_file, get_list_of_files, download_file

# --- Configuration ---
api_key = os.environ.get("GOOGLE_API_KEY")
if api_key is None:
    raise ValueError("GOOGLE_API_KEY environment variable not set.")
genai.configure(api_key=api_key)

app = Flask(__name__) 
BUCKET_NAME = os.getenv("BUCKET_NAME", "images_lee")
IMAGES_PREFIX = "images/"

generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "application/json",
}

model = genai.GenerativeModel(model_name="gemini-1.5-flash")
PROMPT = "give the image a title and briefly describe the image. end your response in json"


# --- Utility Functions ---
def upload_to_gemini(path, mime_type=None):
    """Uploads a file to Gemini and returns the uploaded file object."""
    file = genai.upload_file(path, mime_type=mime_type)
    print(f"Uploaded file '{file.display_name}' as: {file.uri}")
    return file


def extract_json_from_response(response_text):
    """
    Extracts a JSON code block from a response that may contain extra text.
    It looks for a block starting with "json" and ending with "".
    """
    start_token = "json"
    end_token = ""
    start = response_text.find(start_token)
    if start != -1:
        start += len(start_token)
        end = response_text.find(end_token, start)
        if end != -1:
            return response_text[start:end].strip()
    return response_text.strip()


def list_files(bucket_name):
    """Lists all the image files (JPEG) in the bucket."""
    files = get_list_of_files(bucket_name, prefix=IMAGES_PREFIX)
    jpegs = [file for file in files if file.lower().endswith((".jpeg", ".jpg"))]
    return jpegs


# --- Route Handlers ---
@app.route("/")
def index():
    """Displays the main index page with an upload form and a list of files."""
    index_html = """ 
<h1>Course Project</h1>
<form method="post" enctype="multipart/form-data" action="/upload">
  <div>
    <label for="file">Choose file to upload</label>
    <input type="file" id="file" name="form_file" accept="image/jpeg"/>
  </div>
  <div>
    <button>Submit</button>
  </div>
</form>
<ul>
    """
    for file in list_files(BUCKET_NAME):
        index_html += f'<li><a href="/files/{file}">{file}</a></li>'
    index_html += "</ul>"
    return index_html


@app.route("/upload", methods=["POST"])
def upload():
    """Handles file uploads, processes them with Gemini, and stores results."""
    try:
        print("POST /upload")
        file = request.files["form_file"]
        filename = file.filename
        temp_filepath = filename
        file.save(temp_filepath)
        upload_file(BUCKET_NAME, filename, prefix=IMAGES_PREFIX)

        uploaded_file = upload_to_gemini(temp_filepath, mime_type="image/jpeg")
        response = model.generate_content([uploaded_file, "\n\n", PROMPT])
        print("Gemini response:", response.text)

        extracted_json_text = extract_json_from_response(response.text)
        print("Extracted JSON:", extracted_json_text)
        try:
            parsed_response = json.loads(extracted_json_text)
        except json.JSONDecodeError as e:
            print("Error decoding extracted JSON:", e)
            raise ValueError("Gemini API returned an invalid JSON response")

        base_name, _ = os.path.splitext(filename)
        json_filename = base_name + ".json"
        json_filepath = json_filename

        with open(json_filepath, "w") as f:
            json.dump(parsed_response, f)
        upload_file(BUCKET_NAME, json_filename, prefix=IMAGES_PREFIX)

        os.remove(temp_filepath)
        os.remove(json_filepath)

        return redirect("/files/" + filename)

    except Exception as e:
        traceback.print_exc()
        sys.stderr.flush()
        sys.stdout.flush()
        return "An error occurred during upload.", 500


@app.route("/files/<filename>")
def get_file(filename):
    """Displays the image and its description based on the JSON file."""
    print("GET /files/" + filename)
    try:
        base_name, _ = os.path.splitext(filename)
        json_filename = base_name + ".json"
        download_file(BUCKET_NAME, json_filename, prefix=IMAGES_PREFIX)
        with open(json_filename, "r") as file:
            file_contents = file.read()
            print("JSON file contents:", file_contents)
            json_data = json.loads(file_contents)
            title = json_data.get("title", "No Title Found")
            description = json_data.get("description", "No Description Found")
        os.remove(json_filename)
    except Exception as e:
        print(f"Error processing JSON: {e}")
        title = "Error: Could not process image description"
        description = "An error occurred while trying to get the description."

    image_html = f"<h2>{title}</h2>"
    image_html += f'<img src="/image/{filename}" width="500" height="333"><br>{filename}'
    image_html += f"<p>{description}</p>"
    image_html += '<p><a href="/">Back</a></p>'
    return image_html


@app.route("/image/<filename>")
def get_image(filename):
    """Serves the image file."""
    print("GET /image/" + filename)
    download_file(BUCKET_NAME, filename, prefix=IMAGES_PREFIX)
    return send_file(filename)


# --- Main ---
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
