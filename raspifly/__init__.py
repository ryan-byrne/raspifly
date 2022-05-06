from time import sleep, time
from threading import Thread
from gpiozero import DistanceSensor, Servo, Device
from gpiozero.pins.pigpio import PiGPIOFactory
import smbus, math

PWR_MGT_1 = 0x6B
CONFIG = 0x1A 
SAMPLE_RATE = 0x19
GYRO_CONFIG = 0x1B
ACCEL_CONFIG = 0x1C

ACCEL_X_HIGH = 0x3B
ACCEL_Y_HIGH = 0x3D
ACCEL_Z_HIGH = 0x3F

GYRO_X_HIGH = 0x43
GYRO_Y_HIGH = 0x45
GYRO_Z_HIGH = 0x47

TEMP_OUT_HIGH = 0x41

ACCEL_FULL_SCALES = [2, 4, 8, 16]
GYRO_FULL_SCALES = [250, 500, 1000, 2000]

class MPU6050():

    def __init__(self, address=0x68, channel=1, accelerometer_range=0, gyrometer_range=0):

        print(f"Initializing MPU6050 at channel: {channel} and address: {address}...")

        # Setting I2C bus channel and address
        self._bus = smbus.SMBus(channel)
        self._ADDRESS = address

        # Setting Accelerometer and Gyroscope Ranges
        self._accel_range = ACCEL_FULL_SCALES[accelerometer_range]
        self._gyro_range = ACCEL_FULL_SCALES[gyrometer_range]

        # Setting initial telemetry values
        self.roll = 0
        self.pitch = 0
        self.roll_vel = 0
        self.pitch_vel = 0

        # Zeroing Offsets
        self.ROLL_OFFSET = 0.00
        self.PITCH_OFFSET = 0.00
        self.ROLL_VEL_OFFSET = 0.00
        self.PITCH_VEL_OFFSET = 0.00

        try:
            self._write(PWR_MGT_1, 1)
            self._write(CONFIG, 0)
            self._write(SAMPLE_RATE, 7)
            # TODO: Set ranges
            #self._write(ACCEL_CONFIG, accelerometer_range)
            #self._write(GYRO_CONFIG, gyrometer_range)
            self._calculate_offsets()
            self.active = True
            Thread(target=self._accel_thread).start()
        except:
            raise OSError(f"Failed to Initialize MPU6050 (address={address}, channel={channel})")

    def _calculate_offsets(self):

        print("\tCalculating Accelerometer Value Offsets...")

        _roll, _pitch, _roll_vel, _pitch_vel = [], [], [], []

        def _average(list):
            return sum(list) / len(list)

        for i in range(500):
            self._update_values()
            _roll.append(self.roll)
            _pitch.append(self.pitch)
            _roll_vel.append(self.roll_vel)
            _pitch_vel.append(self.pitch_vel)

        self.ROLL_OFFSET = _average(_roll)
        self.PITCH_OFFSET = _average(_pitch)
        self.ROLL_VEL_OFFSET = _average(_roll_vel)
        self.PITCH_VEL_OFFSET = _average(_pitch_vel)

        print(
            f"""
            Roll Offset: {self.ROLL_OFFSET}
            Pitch Offset: {self.PITCH_OFFSET}
            Roll Velocity Offset: {self.ROLL_VEL_OFFSET}
            Pitch Velocity Offset: {self.PITCH_VEL_OFFSET}
            """
        )

    def _accel_thread(self):

        print("\tStarting data acquisition thread...")

        while self.active:
            try:
                self._update_values()
            except Exception as e:
                print(e)
                # TODO: Better warning message
                continue
    
    def _update_values(self):
        self.roll = -math.pi * math.sin( 2 * math.pi * self._read(ACCEL_X_HIGH)/ 65536) - self.ROLL_OFFSET
        self.pitch = -math.pi * math.sin( 2 * math.pi * self._read(ACCEL_Y_HIGH)/ 65536) - self.PITCH_OFFSET
        self.roll_vel = 250/180*math.pi * math.sin( math.pi * self._read(GYRO_Y_HIGH) / 32768) - self.ROLL_VEL_OFFSET
        self.pitch_vel = 250/180*math.pi * math.sin( math.pi * self._read(GYRO_X_HIGH) / 32768) - self.PITCH_VEL_OFFSET
        self.yaw_vel = self._read(GYRO_Z_HIGH)

    
    def _write(self, addr, cmd):
        self._bus.write_byte_data(self._ADDRESS, addr, cmd)

    def _read(self, addr):
        return (self._bus.read_byte_data(self._ADDRESS, addr)<<8)|self._bus.read_byte_data(self._ADDRESS, addr+1)

    def _update(self):
        pass

    def close(self):
        self.active = False
        self._write(PWR_MGT_1, 0)

class Raspifly():

    def __init__(self):

        """Class for Drone Control using Python     
        """

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
            ultrasonic_trig_pin=24
    ):
        print("Starting Raspifly...")
        # Initialize Inputs
        self._initialize_inputs(ultrasonic_echo_pin, ultrasonic_trig_pin)
        # Initialize Motors
        self._initialize_motors(front_right_motor_pin, front_left_motor_pin, back_right_motor_pin, back_left_motor_pin)
        
        self.active = True

        Thread(target=self._main_control_loop).start()

    def stop(self):

        self.active = False

        print("Shutting down Raspifly...")

        for _device in ['_front_right','_front_left','_back_left','_back_right','accelerometer', 'ultrasonic_sensor']:
            print(f"\tClosing {_device}")
            getattr(self, _device).close()

    def _main_control_loop(self):
        """
        This is where the motor control code will go
        """
        while self.active:
            sleep(0.1)

    def _initialize_inputs(self, _echo, _trig):

        print("Initializing Inputs...")

        print(f"\tInitializing Ultrasonic Sensor with Echo={_echo} and Trig={_trig}")
        self.ultrasonic_sensor = DistanceSensor(_echo, _trig, max_distance=5.0, pin_factory=self._factory)

        print(f"\tInitializing Accelerometer on the I2C Bus")
        self.accelerometer = MPU6050()


    def _initialize_motors(self, *pins):

        print("Initializing Motors...")
        
        for i, _motor in enumerate(['_front_right','_front_left','_back_left','_back_right']):
            print(f"\tInitializing {_motor} at pin: {pins[i]}")
            _m = Servo(pins[i], pin_factory=self._factory)
            setattr(self, _motor, _m)