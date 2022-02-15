from distutils.log import debug
from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return "Hello world"

def main():
    app.run(debug=True)