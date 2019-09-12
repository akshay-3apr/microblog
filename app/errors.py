from flask import render_template
from app import project,db

@project.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'),404

@project.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('505.html'),500