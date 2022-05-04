import argparse
from .api import server

def _get__server_args():
    
    parser = argparse.ArgumentParser(description='Raspifly Control Server')
    
    parser.add_argument('--host', nargs="?", default="10.182.15.22" ,help="Set hostname for Raspifly Server")
    parser.add_argument('--port', nargs="?", default="5000", help="Set port for Rapsifly Server")
    parser.add_argument('-d', '--debug', dest="debug", action="store_true", help="Run the server in 'Debugging Mode'")
    parser.add_argument('-s', '--sim', dest="sim", help="Run in 'Simulation Mode'")

    return parser.parse_args()

def raspifly_server():

    # Retrieve Command Line Arguments
    args = _get__server_args()
    # Start the server
    server.run(debug=args.debug, host=args.host, port=args.port)