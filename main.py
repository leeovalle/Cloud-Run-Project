import os
from flask import Flask, redirect, request, send_file
from storage import upload_file, get_list_of_files, download_file  

app = Flask(__name__)
BUCKET_NAME = "images_lee"
IMAGES_PREFIX = "images/"  


os.makedirs('files', exist_ok=True)

@app.route('/')
def index():
    index_html = """
<form method="post" enctype="multipart/form-data" action="/upload" method="post">
  <div>
    <label for="file">Choose file to upload</label>
    <input type="file" id="file" name="form_file" accept="image/jpeg"/>
  </div>
  <div>
    <button>Submit</button>
  </div>
</form>"""

    for file in list_files(BUCKET_NAME):  
        index_html += "<li><a href=\"/files/" + file + "\">" + file + "</a></li>"

    return index_html

@app.route('/upload', methods=["POST"])
def upload():
    file = request.files['form_file']
    file.save(file.filename)

    upload_file(BUCKET_NAME, file.filename, prefix=IMAGES_PREFIX) 

    return redirect("/")

@app.route('/files') 
def list_files_unused(bucket_name): 
    pass

@app.route('/files/<filename>')
def get_file(filename):

    download_file(BUCKET_NAME, filename, prefix=IMAGES_PREFIX) 
    return send_file(filename)


def list_files(bucket_name): 
    """Lists all the blobs in the bucket."""  
    files = get_list_of_files(bucket_name, prefix=IMAGES_PREFIX) 
    jpegs = []
    for file in files:
        if file.lower().endswith(".jpeg") or file.lower().endswith(".jpg"):
            jpegs.append(file)
    return jpegs


if __name__ == '__main__':
    app.run(debug=True)
