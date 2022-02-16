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

    def send_serial_msg():
        pass

    def recieve_serial_msg():
        pass

    def get_telemetry(self, fields):
        return { field:getattr(self, field) for field in fields }