from flask import Blueprint

api = Blueprint('api', __name__)

@api.route('/api/')
def main_api():
    return "api v1"