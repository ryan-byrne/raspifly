from flask import Blueprint, jsonify, request
from ..devices import Drone

apiv1 = Blueprint('api', __name__, url_prefix='/api/v1')

# Drone Class
drone = Drone()

@apiv1.route('/status/', methods=['GET'])
def status():
    return jsonify(drone.status())

@apiv1.route('/startup/', methods=['POST'])
def startup():
    return drone.start(**{})