Install following packages:
pip install flask
pip install flask-wtf
pip install flask-sqlalchemy
pip install flask-migrate
pip install flask-login
pip install flask-uploads
pip install flask-moment
pip install face_recognition
pip install flask-bootstrap

set env variables before starting flask project:
=> $ set FLASK_APP=microblog.py
=> $ set FLASK_ENV=development
=> flask run

The "flask db" sub-command is added by Flask-Migrate to manage everything related to database migrations. 
We create the migration repository for microblog by running:
=> $ flask db init


To generate a migration automatically, Alembic compares the database schema as defined by the database models, against the actual database schema currently used in the database. It then populates the migration script with the changes necessary to make the database schema match the application models. In this case, since there is no previous database, the automatic migration will add the entire User model to the migration script. 
The "flask db migrate" sub-command generates these automatic migrations:
=> $ flask db migrate -m "users table" #(-m is small descriptive comment for added and its optional)
=> $ flask db migrate -m "post table"
=> $ flask db migrate -m "faceImages table"
=> $ flask db migrate -m "faceEncodings table"

The "flask db migrate" command does not make any changes to the database, it just generates the migration script. To apply the changes to the database, the "flask db upgrade" command must be used.
=> $ flask db upgrade

The "flask shell" command is another very useful tool in the flask umbrella of commands. The shell command is the second "core" command implemented by Flask, after run. The purpose of this command is to start a Python interpreter in the context of the application.
=> $ flask shell


The "app.shell_context_processor" decorator registers the function as a shell context function. When the flask shell command runs, it will invoke this function and register the items returned by it in the shell session. The reason the function returns a dictionary and not a list is that for each item you have to also provide a name under which it will be referenced in the shell, which is given by the dictionary keys.

If you try the above and get NameError exceptions when you access db, User and Post, then the make_shell_context() function is not being registered with Flask. The most likely cause of this is that you have not set FLASK_APP=microblog.py in the environment.