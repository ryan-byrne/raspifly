from flask import Blueprint, jsonify, request
from ..devices import Drone

apiv1 = Blueprint('api', __name__, url_prefix='/api/v1')

# Drone Class
drone = Drone()

@apiv1.route('/info/', methods=['GET'])
def info():
		return jsonify({
			"version":"0.0.1",
			"title":"Raspifly API",
			"license":{
					"name":"MIT"
			}
		})

@apiv1.route('/openapi/', methods=['GET'])
def openapi():
		return "3.0.0"

@apiv1.route('/configuration/', methods=['GET','POST'])
@apiv1.route('/configuration/<setting>', methods=['GET','POST'])
def configuration(setting=''):
	if request.method == 'GET' and setting == '':
		return jsonify(drone.configuration)
	elif request.method == 'GET' and setting:
		return jsonify(drone.configuration[setting])
	elif setting and request.method == 'POST':
		return jsonify({"message":drone.set_configuration(request.form, setting)})
	else:
		return jsonify({"message":drone.set_configuration(request.form)})