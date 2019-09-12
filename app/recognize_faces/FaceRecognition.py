import face_recognition
import cv2
import numpy as np
from flask import url_for
from app import project,db
from app.models import User,Face_encodings,Face_Images
from app.config import Config
from app.dbOperation import DBOperations
from PIL import Image
import base64,json,os,traceback
from sqlalchemy import exc

class FaceRecognition:

    known_face_encodings = []
    known_face_names = []

    def face_encoding(self,image):
        #image = face_recognition.load_image_file('app'+url)
        face_image = Image.open(image).convert('RGB')
        image_face_encoding = face_recognition.face_encodings(np.asarray(face_image))[0]
        return image_face_encoding

    def load_face_encodings(self,username):
        # Create arrays of known face encodings and their names
        encoding_tuple = Face_encodings.query.filter_by(username=username).first()
        self.known_face_encodings = [np.fromstring(encoding_tuple.face_encodings,dtype = encoding_tuple.npDtype)]
        self.known_face_names = [encoding_tuple.username]

    def detectFaces(self,image):
        #face_image = face_recognition.load_image_file(image)
        # print('Inside Detect Faces')
        # print(image)
        file = image
        #convert string data to numpy array
        face_image = Image.open(file).convert('RGB')
        face_image_loc = face_recognition.face_locations(np.asarray(face_image))
        #print(face_image_loc)
        if len(face_image_loc)==1:
            return True
        else:
            return False
        # You can access the actual face itself like this:
        # top, right, bottom, left = face_image_loc[0]
        # face_image = face_image_loc[top:bottom, left:right]
        # pil_image = Image.fromarray(face_image)



    def preprocessing(self,username):    

        # Initialize some variables
        face_locations = []
        face_encodings = []
        face_names = []
        
        self.load_face_encodings(username)
        #print('known_face_encodings: ',self.known_face_encodings)

        # Grab a single frame of video
        frame = cv2.imread(Config.UPLOADS_DEFAULT_DEST+Config.FACE_ID)

        # Resize frame of video to 1/4 size for faster face recognition processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_small_frame = small_frame[:, :, ::-1]

        # Find all the faces and face encodings in the current frame of video
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_names = []
        for face_encoding in face_encodings:
            # See if the face is a match for the known face(s)
            matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
            name = "Unknown"

            # # If a match was found in known_face_encodings, just use the first one.
            if True in matches:
                first_match_index = matches.index(True)
                name = self.known_face_names[first_match_index]

            # Or instead, use the known face with the smallest distance to the new face
            # face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            # best_match_index = np.argmin(face_distances)
            # if matches[best_match_index]:
            #     name = known_face_names[best_match_index]
            if username==name:
                face_names.append(name)
            
        return face_names
