import argparse
from .server import app

def _get_server_args():
    
    parser = argparse.ArgumentParser(description='Raspifly Control Server')
    
    parser.add_argument('--host', nargs="?", default="127.0.0.1" ,help="Set hostname for Raspifly Server")
    parser.add_argument('--port', nargs="?", default="5000", help="Set port for Rapsifly Server")
    parser.add_argument('-d', '--debug', dest="debug", action="store_true", help="Run the server in 'Debugging Mode'")
    parser.add_argument('-s', '--sim', dest="sim", action="store_true", help="Run in 'Simulation Mode'")

    return parser.parse_args()

def server():
    # Retrieve Command Line Arguments
    args = _get_server_args()
    # Start the server
    app.run(debug=args.debug, host=args.host, port=args.port)