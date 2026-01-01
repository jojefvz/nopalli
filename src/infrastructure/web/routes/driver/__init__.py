from flask import Blueprint

bp = Blueprint('driver', __name__)

from . import routes