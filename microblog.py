from app import project,db
from app.models import User, Post,Face_encodings,Face_Images

@project.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Post': Post, 'Face_encodings' : Face_encodings,'Face_Images':Face_Images}