from time import sleep, time
from threading import Thread
from gpiozero import DistanceSensor, Servo
from gpiozero.pins.pigpio import PiGPIOFactory
import numpy as np
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
        self.ROLL_OFFSET = 0.0
        self.PITCH_OFFSET = 0.0
        self.YAW_OFFSET = 0.0
        self.ROLL_VEL_OFFSET = 0.0
        self.PITCH_VEL_OFFSET = 0.0
        self.YAW_VEL_OFFSET = 0.0

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

        # TODO: Improve 

        print("\tCalculating Accelerometer Value Offsets...")

        _roll, _pitch, _roll_vel, _pitch_vel = [], [], [], []

        def _average(list):
            return sum(list) / len(list)

        for i in range(100):
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

        print("\tStarting MPU6050 data acquisition thread...")

        while self.active:
            try:
                self._update_values()
            except Exception as e:
                print(e)
                # TODO: Better warning message
                continue

    def _update_values(self):
        self.roll = -math.pi / 2 * math.sin( math.pi * self._read(ACCEL_X_HIGH)/ 32768) - self.ROLL_OFFSET
        self.pitch = -math.pi / 2 * math.sin( math.pi * self._read(ACCEL_Y_HIGH)/ 32768) - self.PITCH_OFFSET
        self.yaw = -math.pi / 2 * math.sin( math.pi * self._read(ACCEL_Z_HIGH)/ 32768) - self.YAW_OFFSET
        self.roll_vel = 250/180 * math.pi * math.sin( math.pi * self._read(GYRO_Y_HIGH) / 32768) - self.ROLL_VEL_OFFSET
        self.pitch_vel = 250/180 * math.pi * math.sin( math.pi * self._read(GYRO_X_HIGH) / 32768) - self.PITCH_VEL_OFFSET
        self.yaw_vel = 250/180 * math.pi * math.sin( math.pi * self._read(GYRO_Z_HIGH) / 32768) - self.YAW_VEL_OFFSET
    
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

    def __init__(self, mass=0.5, length=167, width=167, hover_power=30, layout='x', p_gain=4.0, i_gain=4.0, d_gain=4.0, hz=40):

        """Class for Drone Control using Python     
        """
        self._hover_power = hover_power # Motor Power required to hover (%)
        self._mass = mass # Mass of the drone (kg)
        self._dim = [length/1000, width/1000] # Dimensions of Drone (mm -> m)
        self._p_gain = p_gain # Proportional Gain
        self._read_rate = 1/hz # Rate to send commands to the motors
        self._factory = PiGPIOFactory() # Set the pin factory

        self.active = False # Control Loop Active
    
    def start(self, motor_pins=[5, 6, 13, 19], us_echo_pin=23, us_trig_pin=24):
        print("Starting Raspifly...")
        # Initialize Inputs
        self._initialize_inputs(us_echo_pin, us_trig_pin)
        # Initialize Motors
        self._initialize_motors(motor_pins)
        
        self.active = True

        Thread(target=self._main_control_loop).start()

    def stop(self):

        self.active = False

        print("Shutting down Raspifly...")

        print("Closing Motors")
        [_motor.close() for _motor in self._motors]

        print("Closing Accelerometer")
        self.accelerometer.close()

        print("Closing Ultrasonic Sensor")
        self.ultrasonic_sensor.close()

    def _main_control_loop(self):

        while self.active:

            self._pid_controller()

            sleep(self._read_rate)

    def _pid_controller(self):

        # Target Roll, Pitch, and Yaw Velocities
        target = [
            [0.0],
            [0.0],
            [0.0]
        ]

        # Actuall Roll, Pitch and Yaw Velocities
        current = [
            [self.accelerometer.roll_vel],
            [self.accelerometer.pitch_vel],
            [self.accelerometer.yaw_vel]
        ]

        # Calculate Error
        error = np.subtract( current, target )

        # P Controller

        # I Controller

        # D Controller



    def _thrust_to_signal(self, thrust):
        return 1044 + 277*thrust + -47.1*thrust**2 + 4.07*thrust**3

    def _initialize_inputs(self, _echo, _trig):

        print("Initializing Inputs...")

        print(f"\tInitializing Ultrasonic Sensor with Echo={_echo} and Trig={_trig}")
        self.ultrasonic_sensor = DistanceSensor(_echo, _trig, max_distance=5.0, pin_factory=self._factory)

        print(f"\tInitializing Accelerometer on the I2C Bus")
        self.accelerometer = MPU6050()

    def set_motor_speed(self, motor=None, percent_speed=None):

        self._motors[motor].value = percent_speed / 50 - 1

    def calibrate_motors(self, 
            min_pulse=1000, 
            max_pulse=2000,
            pins=[5,6,13,19]
        ):

        input("Plug in the Raspberry Pi, power down the motors, then Press Enter to Begin Motor Calibration")

        self._initialize_motors(pins)

        print("Setting Maximum Throttle...")

        for motor in [self._front_right,self._front_left,self._back_left,self._back_right]:
            motor.value = max_pulse / 750 - 2

        input("Power on your ESCs. Press Enter to after Beeps")

        print("Setting Minimum Calibration")

        for motor in [self._front_right,self._front_left,self._back_left,self._back_right]:
            motor.value = min_pulse / 750 - 2

        print('Motor Calibration Complete.')

    def _initialize_motors(self, pins):

        print("Initializing Motors...")

        self._motors = []

        for pin in pins:
            self._motors.append( Servo(pin, pin_factory=self._factory) )