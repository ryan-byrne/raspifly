from time import sleep
from threading import Thread
from gpiozero import DistanceSensor, Servo, Device
from gpiozero.pins.pigpio import PiGPIOFactory

DEFAULT_TELEMETRY_FIELDS = [
    'x_pos','y_pos','z_pos',
    'x_vel','y_vel','z_vel',
    'x_acc','y_acc','z_acc',
    'roll','pitch','yaw',
    'roll_vel','pitch_vel','yaw_vel',
    'roll_acc','pitch_acc','yaw_acc',
]

class Raspifly():

    def __init__(self):

        """Class for Drone Control using Python     
        """
        # Set initial value of 0 for each telemetry field
        [setattr(self, field, 0) for field in DEFAULT_TELEMETRY_FIELDS]
        # Set Pin Factory
        self._factory = PiGPIOFactory()
        self.active = False
    
    def start(
            self,
            front_right_motor_pin=5,
            front_left_motor_pin=6,
            back_right_motor_pin=13,
            back_left_motor_pin=19,
            ultrasonic_echo_pin=23,  
            ultrasonic_trig_pin=24,
            accelerometer_scl_pin=20,
            accelerometer_sda_pin=21
    ):
            # Initialize Inputs
        self._initialize_inputs(ultrasonic_echo_pin, ultrasonic_trig_pin, accelerometer_scl_pin, accelerometer_sda_pin)
        # Initialize Motors
        self._initialize_motors(front_right_motor_pin, front_left_motor_pin, back_right_motor_pin, back_left_motor_pin)
        
        self.active = True

        Thread(target=self._main_control_loop).start()



    def _main_control_loop(self):
        while self.active:
            print({
                "z_pos":self._ultrasonic_sensor.distance,
                'hello':'world'
            })
            sleep(1)
    
    def stop(self):
        self.active = False
        [getattr(self, _device).close() for _device in ['_front_right','_front_left','_back_left','_back_right','_accelerometer','_ultrasonic_sensor']]

    def _initialize_inputs(self, _echo, _trig, _scl, _sda):

        print("Initializing Inputs...")

        print(f"\tInitializing Ultrasonic Sensor with Echo={_echo} and Trig={_trig}")
        self._ultrasonic_sensor = DistanceSensor(_echo, _trig, max_distance=5.0, pin_factory=self._factory)

        print(f"\tInitializing Accelerometer with SCL={_scl} and SDA={_sda}")
        self._accelerometer = DistanceSensor(_scl, _sda, pin_factory=self._factory)
    
    def _initialize_motors(self, *pins):

        print("Initializing Motors...")
        
        for i, _motor in enumerate(['_front_right','_front_left','_back_left','_back_right']):
            print(f"\tInitializing {_motor} at pin: {pins[i]}")
            setattr(self, _motor, Servo(pins[i], pin_factory=self._factory))


    def _update_telemetry(self):
        self.z_pos = self._ultrasonic_sensor.distance

    def get_telemetry(self, fields=[]):

        if len(fields)==0:
            return { field:getattr(self, field) for field in fields }
        else:
            return { field:getattr(self, field) for field in DEFAULT_TELEMETRY_FIELDS }