from flask import Flask, jsonify, request, render_template
from . import Raspifly

# Variable to house the Raspifly class
raspifly = Raspifly()

# FLASK SERVER
server = Flask(__name__, template_folder="./client/build", static_folder="./client/build/static")

@server.route('/api/start', methods=["POST"])
def post_start():
    if not raspifly.active:
        raspifly.start()
        return "Successfully started", 200
    else:
        return "Raspifly is already running", 500


@server.route('/api/stop', methods=["POST"])
def post_stop():
    if raspifly.active:
        raspifly.stop()
        return "Successfully stopped", 200
    else:
        return "Raspifly is not currently running", 500


@server.route('/api/control', methods=["POST"])
def post_control():
    raspifly.control(request.get_json())
    return "Successfully posted", 200

@server.route('/api/telemetry', methods=["GET"])
def get_telemetry():
    return jsonify( raspifly.get_telemetry( request.args.get('fields[]').split(",") ) )

@server.route('/')
def index():
    return render_template('index.html')