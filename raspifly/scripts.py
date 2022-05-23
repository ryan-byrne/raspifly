import argparse

def _get_server_args():
    
    parser = argparse.ArgumentParser(description='Raspifly Control Server')
    
    parser.add_argument('--host', nargs="?", default="10.182.15.38" ,help="Set hostname for Raspifly Server")
    parser.add_argument('--port', nargs="?", default="5000", help="Set port for Rapsifly Server")
    parser.add_argument('-d', '--debug', dest="debug", action="store_true", help="Run the server in 'Debugging Mode'")
    parser.add_argument('-s', '--sim', dest="sim", help="Run in 'Simulation Mode'")

    return parser.parse_args()

def test():
    from . import Raspifly
    print("Test Mode")
    drone = Raspifly()
    input("Start Test?")
    drone.start()
    input("Stop?")
    drone.stop()

def calibrate():
    from . import Raspifly
    print("Calibration Mode")
    drone = Raspifly()
    drone.calibrate_motors()

def server():
    from .api import server as srv
    # Retrieve Command Line Arguments
    args = _get_server_args()
    # Start the server
    srv.run(debug=args.debug, host=args.host, port=args.port)