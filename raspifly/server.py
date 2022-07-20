from flask import Flask, Blueprint, jsonify
from .devices import Drone

# FLASK SERVER
app = Flask(__name__)
# Add Blueprints
api = Blueprint('api', __name__)
app.register_blueprint(api)
# Drone Class
drone = Drone()

@app.route('/')
def index():
    return "Homepage"

@app.route('/api/v1/status/')
def status():
    return jsonify(drone.status())

@app.route('/api/v1/startup')
def startup():
    return drone.start()