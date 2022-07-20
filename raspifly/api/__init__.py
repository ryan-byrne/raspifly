from flask import Blueprint
from . import raspifly

api = Blueprint('api', __name__)

@api.route('/api')
def main_api():
    return "api v1"