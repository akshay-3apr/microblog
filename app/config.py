import os
from pathlib import Path,PurePath

basedir = os.path.abspath(os.path.dirname(__file__))
pathlibBaseDir = Path.cwd()

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'Secret'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FACE_ID = 'cur_face_id.jpeg'
    UPLOADS_DEFAULT_DEST = 'app/static/img/Users/'
    UPLOADS_DEFAULT_URL = 'static/img/Users/'
 
    UPLOADED_IMAGES_DEST = 'app/static/img/Users/'
    UPLOADED_IMAGES_URL = 'static/img/Users/'
    TEMPUSERIMG = pathlibBaseDir / Path('app/static/img/Users/processing')
    IMAGE_STORE = pathlibBaseDir / Path('app/static/img/Users')
    ALLOWED_IMAGE_EXTENSIONS = ["JPEG", "JPG", "PNG", "GIF"]
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['your-email@example.com']
    POSTS_PER_PAGE = 10