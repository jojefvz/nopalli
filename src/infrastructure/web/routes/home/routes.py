from flask import render_template

from src.infrastructure.web.routes.home import bp


@bp.route('/')
def home():
    return render_template("home/home.html")