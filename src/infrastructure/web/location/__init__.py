from flask import Blueprint

bp = Blueprint('location', __name__)

from . import routes