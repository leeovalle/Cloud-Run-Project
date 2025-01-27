import os
import gunicorn
from flask import Flask, redirect, request, send_file
from storage import upload_file, list_files, download_blob  

app = Flask(__name__)
BUCKET_NAME = "images_lee" 
IMAGE_PREFIX = "images/"


@app.route('/')
def index():
    index_html = """
<form method="post" enctype="multipart/form-data" action="/upload">
  <div>
    <label for="file">Choose file to upload</label>
    <input type="file" id="file" name="form_file" accept="image/jpeg"/>
  </div>
  <div>
    <button>Submit</button>
  </div>
</form>
<hr>
<ul>"""

    for file in list_files(BUCKET_NAME, IMAGE_PREFIX):
        index_html += f"<li><a href=\"/files/{file}\">{file}</a></li>"

    index_html += "</ul>"
    return index_html

@app.route('/upload', methods=["POST"])
def upload():
    file = request.files['form_file']
    filename = file.filename

    upload_file(BUCKET_NAME, IMAGE_PREFIX + filename, file)  

    return redirect("/")



@app.route('/files/<filename>')
def get_file(filename):
    full_blob_name = IMAGE_PREFIX + filename

    file_stream, content_type = download_blob(BUCKET_NAME, full_blob_name)

    if file_stream:
        return send_file(file_stream, mimetype=content_type) # Use content_type for correct MIME
    else:
        return "File not found", 404


if __name__ == '__main__':
    app.run(debug=True)
