from flask import Flask, jsonify, request, render_template, Response, stream_with_context
import json, time

# Variable to house the Raspifly class
raspifly = None

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

    def generate():

        while raspifly.active:
            time.sleep(0.1)
            # TODO: Add back US Sensor
            data = json.dumps({
                "pitch":raspifly.accelerometer.pitch,
                "roll":raspifly.accelerometer.roll
            })
            yield f"data:{json.dumps(data)}\n\n"


    response = Response(stream_with_context(generate()), mimetype="text/event-stream")
    response.headers["Cache-Control"] = "no-cache"
    response.headers["X-Accel-Buffering"] = "no"
    
    return response

@server.route('/')
def index():
    return render_template('index.html')