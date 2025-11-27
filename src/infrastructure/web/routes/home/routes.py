from flask import render_template

from ..home import bp


@bp.route('/')
def home():
    return render_template("home/home.html")