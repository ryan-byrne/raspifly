from flask import Blueprint, jsonify, request
from ..devices import Drone

apiv1 = Blueprint('api', __name__, url_prefix='/api/v1')

# Drone Class
drone = Drone()

_OPENAPI = "3.0.0"

_INFO = {
    "version":"0.0.1",
    "title":"Raspifly API",
    "license":{
        "name":"MIT"
    }
}

@apiv1.route('/info/', methods=['GET'])
def info():
		return jsonify(_INFO)

@apiv1.route('/openapi/', methods=['GET'])
def openapi():
		return jsonify(_OPENAPI)

@apiv1.route('/configuration/<setting>', methods=['GET','POST'])
def configuration(setting=None):
	if request.method == 'GET' and not setting:
		return jsonify(drone.configuration)
	elif request.method == 'GET' and setting:
		return jsonify(drone.configuration[setting])
	elif setting:
		return jsonify(drone.set_configuration(request.form, setting))
	else:
		return jsonify(drone.set_configuration(request.form))