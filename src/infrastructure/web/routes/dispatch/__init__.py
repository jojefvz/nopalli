from flask import Blueprint

bp = Blueprint('dispatch', __name__)

from . import routes