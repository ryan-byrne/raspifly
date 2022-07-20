from flask import Flask, Blueprint
from .api import api
# Variable to house the Raspifly class
raspifly = None

# FLASK SERVER
server = Flask(__name__)
# Blueprints
server.register_blueprint(api)

@server.route('/')
def index():
    return "Homepage"