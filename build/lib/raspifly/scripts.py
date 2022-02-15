from . import Raspifly

def raspifly_server():
    print("Inilializing Raspifly Class...")
    raspifly = Raspifly()
    print("Starting Raspifly Server...")
    raspifly.start_server()