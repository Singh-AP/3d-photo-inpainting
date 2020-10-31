import os
from flask import Flask, flash, request, redirect, url_for, render_template, session
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
                session['user_image']=filename
                return redirect(url_for('run',user_image=filename))
            else:
                flash("Kindly upload only .png, .jpg or .jpeg image")
                return redirect(url_for('upload_file'))
    return render_template('index.html')

@app.route('/run', methods=['GET', 'POST'])
def run():
    print(request.method)
    if request.method == 'POST':
        config=yaml.load(open("argument.yml", 'r'))
        session['config_dict'] = config
        """
        if 'run' in request.form:
            print("Calling Main function")
            try:
                config=yaml.load(open("argument.yml", 'r'))
                session['config_dict'] = config
                Main(config)
                print("Main function ended successfully. Cleaning up now")
                cleanup("static",".jpg")
                cleanup("image",".jpg")
            except Exception as e:
                print("Main function raised error.")
                print(e)
        """
        # TODO change to /results
        return redirect(url_for("results"))
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

@app.route('/results',methods=['GET', 'POST'])
def results():
    """
    GET: Display the effects videos, expects config={dict} and user_image={string} in GET message
    """
    print(request.method)
    if request.method == 'GET':
        user_img = session['user_image']
        config = session['config_dict']
        print("user_img is ", user_img)
        vid_names = generate_list_of_vid_names(user_img)
        return render_template("results.html",dolly_vid=vid_names[0],
                zoom_vid=vid_names[1], circle_vid=vid_names[2], swing_vid=vid_names[3])


def generate_list_of_vid_names(vid_name):
    vid_name=os.path.splitext(vid_name)[0]
    ans=[]
    postfix = session['config_dict']["video_postfix"]
    for pf in postfix:
        ans.append(str(vid_name)+"_"+str(pf)+".mp4")
    print("List of vid names: ",ans)
    return ans

def cleanup(directory, ftype):
    files_in_directory = os.listdir(directory)
    filtered_files = [file for file in files_in_directory if file.endswith(ftype)]
    for file in filtered_files:
        path_to_file = os.path.join(directory, file)
        os.remove(path_to_file)


if __name__ == "__main__":
    app.run()