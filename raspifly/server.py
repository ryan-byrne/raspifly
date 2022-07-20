from flask import Flask
from .api import apiv1

# FLASK SERVER
app = Flask(__name__)
# Add Blueprints
app.register_blueprint(apiv1)

@app.route('/')
def index():
    return "Homepage"