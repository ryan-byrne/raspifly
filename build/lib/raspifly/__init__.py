from flask import Flask, jsonify, request, render_template
import time, serial

# CONTROL OBJECT

DEFAULT_TELEMETRY_FIELDS = [
    'x','y'
]

class Raspifly():

    def __init__(self, port=None, baud=9600):

        """Class to communicate between the Raspberry Pi and Arduino
        """

        self.x = 10
        self.y = 0
        self.z = 10

        pass

    def start_server(self):
        # FLASK SERVER
        app = Flask(__name__, template_folder="../client/build", static_folder="../client/build/static")

        @app.route('/api/telemetry', methods=["GET"])
        def get_telemetry(args):
            field_string = request.args.get('fields[]')
            fields = args.split(",") if field_string else DEFAULT_TELEMETRY_FIELDS
            return jsonify(self.get_telemetry(fields))

        @app.route('/')
        def index():
            return render_template('index.html')

        app.run(debug=True)

    def send_serial_msg():
        pass

    def recieve_serial_msg():
        pass

    def get_telemetry(self, fields):
        return { field:getattr(self, field) for field in fields }