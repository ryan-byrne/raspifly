from flask import Flask, jsonify, request, render_template
import raspifly

# Initialize Raspifly Class
rspfly = raspifly.Raspifly()

# FLASK SERVER
app = Flask(__name__, template_folder="../client/build", static_folder="../client/build/static")

@app.route('/api/telemetry', methods=["GET"])
def get_telemetry():
    field_string = request.args.get('fields[]')
    fields = args.split(",") if field_string else raspifly.DEFAULT_TELEMETRY_FIELDS
    return jsonify(rspfly.get_telemetry(fields))

@app.route('/')
def index():
    return render_template('index.html')

def run():
    app.run(debug=True)