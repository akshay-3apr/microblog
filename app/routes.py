from app import project,db
from app.forms import LoginForm,RegistrationForm,EditProfileForm,PostForm
from app.models import User,Post,Face_encodings,Face_Images,Post
from app.config import Config
from app.recognize_faces.FaceRecognition import FaceRecognition
from flask import jsonify, render_template, request,flash, redirect, url_for,send_from_directory
from flask_login import current_user, login_user, logout_user,login_required
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
from PIL import Image
import base64,json,os,traceback,sys
from pathlib import Path
from sqlalchemy import exc
from app import images
from app.dbOperation import DBOperations
from datetime import datetime

@project.route('/login', methods=['GET', 'POST'])
def login():
    print('Inside Login Function')
    if current_user.is_authenticated :
        return redirect(url_for('index'))
    
    form = LoginForm()
    if "imgBase64" in request.values:
        with open('log.txt', 'w') as f:
            f.write(request.values['imgBase64'])
            f.write('Username: '+ request.values['username'])
        #print(request.values)
        data_url = request.values['imgBase64']  
        content = data_url.split(';')[1]
        image_encoded = content.split(',')[1]
        body = base64.b64decode(image_encoded.encode())
        
        loggedInUsername = request.values['username']
        
        with open(Config.UPLOADS_DEFAULT_DEST+Config.FACE_ID, 'wb') as f:
            f.write(body)
        user = {}
        if User.query.filter_by(username=loggedInUsername).first():
            user = match_faces(loggedInUsername)
        else :
            flash('Could not recognize the User, please try logging in using password.'),401
            return jsonify('denied'),400
        
        with open('user.txt', 'w') as f:
            json.dump(user['userList'], f)

        print('Inside Login FACE ID codition check')

        user = User.query.filter_by(username=user['userList'][0]).first()
        if user is not None:
            os.remove(Config.UPLOADS_DEFAULT_DEST+Config.FACE_ID)
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('index')
            return next_page
    
    elif form.validate_on_submit():
        print('Inside Login Function 3')
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@project.route('/',methods=['GET', 'POST'])
@project.route('/index',methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!')
        return redirect(url_for('index'))
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(page,project.config['POSTS_PER_PAGE'],False)
    next_url = url_for('index', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('index', page=posts.prev_num) if posts.has_prev else None
    return render_template('index.html', title='Home', form=form,posts=posts.items, next_url=next_url,prev_url=prev_url)

@project.route('/cameramodal')
def cameramodal():
    return render_template('cameraModal.html')

def match_faces(username):
    ml = FaceRecognition()
    data = {'userList':ml.preprocessing(username)}
    print("data: ",data)
    return data

@project.route('/logout')
def logout():
    print('current_user.is_authenticated: ' + str(current_user.is_authenticated))
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        #db.session.add(current_user)
        db.session.commit()
    logout_user()
    return redirect(url_for('login'))

@project.route('/register',methods=['GET','POST'])
def register():
    dbOpr = DBOperations()
    faceRecog = FaceRecognition()
    #emptyFolder()
    print('inside register function')
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    print(form.validate_on_submit())
    print(form.image.data)
    #print(form.validate())
    if request.method == 'POST':
        print('inside register function POST form submission')
        
        try:
            user = User(username=form.username.data, email=form.email.data,firstname=form.firstname.data,lastname=form.firstname.data,fullname=form.firstname.data +' '+ form.lastname.data)
            user.set_password(form.password.data)
            success = dbOpr.addUser(user)

            emptyFolder(request.files['image'].filename)

            image = request.files['image']
            secure_name = secure_filename(image.filename)
            filename=Image.open(image)
            path = Path(Config.IMAGE_STORE)/user.username
            print(path)
            try:
                path.mkdir()
            except FileExistsError as ex:
                print(ex)
            filename.save(path / secure_name)
            url = images.url(user.username+'/'+image.filename)

            user_id = User.query.filter_by(username=form.username.data).first()
            face_image = Face_Images(username=form.username.data,url=url,filename=secure_name,faceImages=user_id)
            success = dbOpr.addFace_Images(face_image)
            
            # correctUrl = url.replace('http://localhost:5000','')
            # print(correctUrl)
            face_encodings=faceRecog.face_encoding(image=image.stream)
            dtype = face_encodings.dtype.name
            face_encode = Face_encodings(username=form.username.data,face_encodings=face_encodings.tostring(),npDtype=dtype,faceEncoding=user_id)
            success = dbOpr.addFaceEncode(face_encode)

            if success == 'true':
                flash('Congratulations, you are now a registered user!')
                #dbOpr.dbCommit()
            else:
                with open('dbLog.txt','w') as f:
                    f.write(str(success))
                flash('Some Error occured whle registering data into DB')
                return render_template('registrationform.html', title='Register', form=form)
        except exc.SQLAlchemyError:
            #exc_type, exc_value, exc_traceback = sys.exc_info()
            #traceback.print_tb(exc_traceback,file='log.txt')
            return render_template('registrationform.html', title='Register', form=form)

        flash('New User, {}, added and all configuration done!'.format(user.username))
        return redirect(url_for('login'))
    else:
        with open('log.txt', 'w') as f:
            f.write(str({'request.files': request.files,'files':form.image.data,'request.forms':request.form,'request':request.args}))

    return render_template('registrationform.html', title='Register', form=form)

@project.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page=request.args.get('page',1,type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(page,project.config['POSTS_PER_PAGE'],False)
    next_url = url_for('user',username=user.username,page=posts.next_num) if posts.has_next else None
    prev_url = url_for('user',username=user.username,page=posts.prev_num) if posts.has_prev else None
    return render_template('user.html',user=user,posts=posts.items,next_url=next_url,prev_url=prev_url)

# @project.before_request
# def before_request():
#     print()
#     if not current_user.is_authenticated and request.endpoint != 'login':
#         return redirect(url_for('login'))

@project.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)
    
@project.route('/displayImage',methods=['GET','POST'])
def displayImage():
    url=''
    if request.method == 'POST':
        if 'file' in request.files:
            image = request.files['file']
            if image.filename == "":
                print("No filename")
                return redirect(request.url)
            
            if allowed_image(image.filename):
                if(FaceRecognition().detectFaces(image=image.stream)):
                    filename=Image.open(image)
                    secure_name = secure_filename(image.filename)
                    filename.save(Config.TEMPUSERIMG / secure_name)
                    url = images.url('processing/'+image.filename)
                    return jsonify(uploaded_image=url)
                else:
                    return jsonify(error=404,error_msg='There was no face detected in the uploaded image or there are more than 1 face detected in the uploaded image. Please upload again.'),400

            else:
                flash("That file extension is not allowed")
                return redirect(request.url)

def allowed_image(filename):

    if not "." in filename:
        return False

    ext = filename.rsplit(".", 1)[1]

    if ext.upper() in project.config["ALLOWED_IMAGE_EXTENSIONS"]:
        return True
    else:
        return False

def unique_path(directory, name_pattern):
    counter = 0
    while True:
        counter += 1
        path = directory / name_pattern.format(counter)
        if not path.exists():
            return path

def emptyFolder(filename):
    print('Inside emptyFolder')
    folder = Config.TEMPUSERIMG
    print('folder: ',folder)
    for the_file in folder.iterdir():
        print('the_file: ',the_file)
        try:
            if the_file.is_file() and the_file == (Config.TEMPUSERIMG / Path(filename)):
                Path.unlink(the_file)
            #elif os.path.isdir(file_path): shutil.rmtree(file_path)
        except Exception as e:
            print(e)

@project.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot follow yourself!')
        return redirect(url_for('user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('You are following {}!'.format(username))
    return redirect(url_for('user', username=username))

@project.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot unfollow yourself!')
        return redirect(url_for('user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('You are not following {}.'.format(username))
    return redirect(url_for('user', username=username))

@project.route('/explore')
@login_required
def explore():
    page = request.args.get('page',1,type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(page,project.config['POSTS_PER_PAGE'],False)
    next_url = url_for('explore', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('explore', page=posts.prev_num) if posts.has_prev else None
    return render_template("index.html", title='Explore', posts=posts.items,next_url=next_url,prev_url=prev_url)