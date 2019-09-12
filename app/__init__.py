from flask import Flask
from app.config import Config
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_uploads import UploadSet, IMAGES, configure_uploads
import logging
from logging.handlers import SMTPHandler,RotatingFileHandler
import os
#from flask_mail import Mail
from flask_moment import Moment

project = Flask(__name__)
project.config.from_object(Config)

#below code for integrating SQLAlchemy with flask
db=SQLAlchemy(project)
migrate=Migrate(project,db)

#below setting for registering login page
login = LoginManager(project)
login.login_view = 'login'

# Configure the image uploading via Flask-Uploads
images = UploadSet('images', IMAGES)
moment = Moment(project)
configure_uploads(project, images)

Bootstrap(project)

if not project.debug:
    if project.config['MAIL_SERVER']:
        auth = None
        if project.config['MAIL_USERNAME'] or project.config['MAIL_PASSWORD']:
            auth=(project.config['MAIL_USERNAME'],project.config['MAIL_PASSWORD'])
        secure = None
        if project.config['MAIL_USE_TLS']:
            secure = ()
        mail_handler = SMTPHandler(
            mailhost = (project.config['MAIL_SERVER'],project.config['MAIL_PORT']),
            fromaddr = 'no-reply@'+project.config['MAIL_SERVER'],
            toaddrs = project.config['ADMINS'],subject='MicroBlog Failure',
            credentials=auth,secure=secure)
        mail_handler.setLevel(logging.ERROR)
        project.logger.addHandler(mail_handler)
    
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/microblog.log', maxBytes=10240,
                                       backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    project.logger.addHandler(file_handler)

    project.logger.setLevel(logging.INFO)
    project.logger.info('Microblog startup')

from app import routes,models