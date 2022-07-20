import argparse
from . import Raspifly

def _get_server_args():
    
    parser = argparse.ArgumentParser(description='Raspifly Control Server')
    
    parser.add_argument('--host', nargs="?", default="127.0.0.1" ,help="Set hostname for Raspifly Server")
    parser.add_argument('--port', nargs="?", default="5000", help="Set port for Rapsifly Server")
    parser.add_argument('-d', '--debug', dest="debug", action="store_true", help="Run the server in 'Debugging Mode'")
    parser.add_argument('-s', '--sim', dest="sim", action="store_true", help="Run in 'Simulation Mode'")

    return parser.parse_args()

def test():
    print("Test Mode")
    drone = Raspifly()
    print("Start?")
    drone.start()
    print("Stop?")
    drone.stop()

def calibrate():
    print("Calibration Mode")
    drone = Raspifly()
    drone.calibrate_motors()

def server():
    from .server import server
    # Retrieve Command Line Arguments
    args = _get_server_args()

    # Create Raspifly Class and update raspifly variable on server
    server.raspifly = Raspifly(simulation_mode=args.sim)

    # Start the server
    server.run(debug=args.debug, host=args.host, port=args.port)