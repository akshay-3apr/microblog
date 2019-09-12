from app import project,db
from app.models import User,Post,Face_encodings,Face_Images
import json,os,traceback
from sqlalchemy import exc

class DBOperations:
    
    def addUser(self,user):
        try:
            db.session.add(user)
            db.session.commit()
            return 'true'
        except exc.SQLAlchemyError:
            return "An error occured while adding user to the User table: {}".format(traceback.format_exc())

    def addPost(self,post):
        try:
            db.session.add(post)
            db.session.commit()
            return 'true'
        except exc.SQLAlchemyError:
            return "An error occured while adding Post to the Post table: {}".format(traceback.format_exc())

    def addFaceEncode(self,face_encode):
        try:
            db.session.add(face_encode)
            db.session.commit()
            return 'true'
        except exc.SQLAlchemyError:
            return "An error occured while storing face_encode to the Face_encoding table: {}".format(traceback.format_exc())

    def addFace_Images(self,face_images):
        try:
            db.session.add(face_images)
            db.session.commit()
            return 'true'
        except exc.SQLAlchemyError:
            return "An error occured while storing face_images to the Face_Images table: {}".format(traceback.format_exc())

    def dbCommit(self):
        db.session.commit()