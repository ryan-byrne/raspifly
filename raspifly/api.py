from flask import Flask, jsonify, request, render_template
from . import Raspifly, DEFAULT_TELEMETRY_FIELDS

# Initialized Raspifly Class
raspifly = Raspifly()

# FLASK SERVER
server = Flask(__name__, template_folder="../client/build", static_folder="../client/build/static")

@server.route('/api/control', methods=["POST"])
def send_control():
    return "", 200

@server.route('/api/telemetry', methods=["GET"])
def get_telemetry():
    field_string = request.args.get('fields[]')
    fields = field_string.split(",") if field_string else DEFAULT_TELEMETRY_FIELDS
    return jsonify(raspifly.get_telemetry(fields))

@server.route('/')
def index():
    return render_template('index.html')