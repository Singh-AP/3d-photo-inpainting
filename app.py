import os
from flask import Flask, flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
from main import Main
import json
import os
import shutil
import yaml

# UPLOAD_FOLDER = os.path.dirname(os.path.realpath(__file__))+'/image'
UPLOAD_FOLDER = './image'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = "super secret key"


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET','POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file:
            if allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                shutil.copyfile("image/"+filename, "static/"+filename)
                file_json = json.dumps({"user_img":str(filename)})
                return redirect(url_for('run',user_image=filename))
            else:
                flash("Kindly upload only .png, .jpg or .jpeg image")
                return redirect(url_for('upload_file'))
    return render_template('index.html')

@app.route('/run', methods=['GET', 'POST'])
def run():
    print(request.method)
    if request.method == 'POST':
        # if request.form.validate_on_submit():
        if 'run' in request.form:
            print("Calling Main function")
            try:
                config=yaml.load(open("argument.yml", 'r'))
                Main(config)
                print("Main function ended successfully. Cleaning up now")
                cleanup("static",".jpg")
                cleanup("image",".jpg")
            except Exception as e:
                print("Main function raised error.")
                print(e)
        return render_template("index.html")
        # if request.form.get('Encrypt') == 'Encrypt':
        #     # pass
        #     print("Encrypted")
        # elif  request.form.get('Decrypt') == 'Decrypt':
        #     # pass # do something else
        #     print("Decrypted")
        # else:
        #     # pass # unknown
        #     return render_template("index.html")
    elif request.method == 'GET':
        user_img = request.args["user_image"]
        print("user_img is ", user_img)
        # full_filename = os.path.join(app.config['UPLOAD_FOLDER'], user_img)
        return render_template("user_run.html", user_image=user_img)

def cleanup(directory, ftype):
    files_in_directory = os.listdir(directory)
    filtered_files = [file for file in files_in_directory if file.endswith(ftype)]
    for file in filtered_files:
        path_to_file = os.path.join(directory, file)
        os.remove(path_to_file)


if __name__ == "__main__":
    app.run()