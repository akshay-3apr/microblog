from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,BooleanField,SubmitField,TextAreaField
from wtforms.validators import Required,Email,DataRequired,ValidationError,EqualTo,Length
from flask_wtf.file import FileField, FileAllowed, FileRequired
from app.models import User
from flask import app
from app import images

class LoginForm(FlaskForm):
    username = StringField('Email Address', validators=[Required(),DataRequired()])
    password = PasswordField('Password', validators=[Required(),DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')
    camera = StringField('Login with Face ID')

class RegistrationForm(FlaskForm):
    firstname = StringField('Firstname',validators=[DataRequired()])
    lastname = StringField('Lastname',validators=[DataRequired()])
    username = StringField('Username',validators=[DataRequired()])
    email = StringField('Email',validators=[DataRequired(),Email()])
    password = PasswordField('Password',validators=[DataRequired()])
    password2 = PasswordField('Confirm Password',validators=[DataRequired(),EqualTo('password',message='Confirm Password must match Password field')])
    image = FileField('Upload Image for Face ID',validators=[FileRequired(),FileAllowed(['jpg', 'png','jpeg'], 'Images only!')])
    # validators=[FileRequired(),FileAllowed(images, 'Images only!')]
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username = username.data).first()
        if user is not None:
            raise ValidationError('Please Use a different Username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is  not None:
            raise(ValidationError('Please use a different email address. This email already exists in the system.'))

class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username. This name is already taken')

class PostForm(FlaskForm):
    post = TextAreaField('Say something', validators=[DataRequired(), Length(min=1, max=140)])
    submit = SubmitField('Submit')