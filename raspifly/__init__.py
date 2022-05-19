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

    def __init__(self, address=0x68, channel=1, accelerometer_range=0, gyrometer_range=0, sample_rate=100):

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

        self._sample_rate = sample_rate # Hz

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

        sleep(1/self._sample_rate)
    
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

    def __init__(self, mass=0.5, length=167, width=167, hover_power=30, layout='x', p_gain=4.0, i_gain=4.0, d_gain=4.0, hz=40, us_echo_pin=23, us_trig_pin=24, motor_pins=[5, 6, 13, 19]):

        """Class for Drone Control using Python     
        """
        self._hover_power = hover_power # Motor Power required to hover (%)
        self._mass = mass # Mass of the drone (kg)
        self._dim = [length/1000, width/1000] # Dimensions of Drone (mm -> m)
        self._p_gain = p_gain # Proportional Gain
        self._read_rate = 1/hz # Rate to send commands to the motors
        print("Importing PiGPIO Factory...")
        self._factory = PiGPIOFactory() # Set the pin factory
        self.active = False # Control Loop Active

        # Initialize Motors
        self._initialize_motors(motor_pins)
        self.motor_speeds = [0.0, 0.0, 0.0, 0.0]

        print(f"\tInitializing Ultrasonic Sensor with Echo={us_echo_pin} and Trig={us_trig_pin}")
        self.ultrasonic_sensor = DistanceSensor(us_echo_pin, us_trig_pin, max_distance=5.0, pin_factory=self._factory)

        print(f"\tInitializing Accelerometer on the I2C Bus")
        self.accelerometer = MPU6050()
    
    def start(self):
        
        print("Starting Raspifly...")
        
        self.active = True

        Thread(target=self._main_control_loop).start()

    def stop(self):

        self.active = False

        print("Shutting down Raspifly...")

        print("Closing Motors")
        self.stop_motors()

        print("Closing Accelerometer")
        self.accelerometer.close()

        print("Closing Ultrasonic Sensor")
        self.ultrasonic_sensor.close()

    def stop_motors(self):
        [_motor.close() for _motor in self._motors]

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
        actual = [
            [self.accelerometer.roll_vel],
            [self.accelerometer.pitch_vel],
            [self.accelerometer.yaw_vel]
        ]

        error = np.subtract( target, actual )

        # P Controller

        P = self._p_gain * error

        # I Controller

        # D Controller

        self.motor_speeds = [30.0, 30.0, 30.0, 30.0]

        [self.set_motor_speed(i, speed) for i, speed in enumerate(self.motor_speeds)]

    def set_motor_speed(self, motor=None, percent_speed=None):
        self._motors[motor].value = percent_speed / 50 - 1

    def calibrate_motors(self, 
            min_pulse=1000, 
            max_pulse=2000,
            motor_pins=[5, 6, 13, 19]
        ):

        self._initialize_motors(motor_pins)

        input("Plug in the Raspberry Pi, power down the motors, then Press Enter to Begin Motor Calibration")

        print("Setting Maximum Throttle...")

        for motor in self._motors:
            motor.value = max_pulse / 750 - 2

        input("Power on your ESCs. Press Enter after Beeping stops")

        print("Setting Minimum Calibration")

        for motor in self._motors:
            motor.value = min_pulse / 750 - 2

        input("Press Enter after beeping stops.")

        print('Motor Calibration Complete. Shutting Down Motors')

        for motor in self._motors:
            motor.close()

    def _initialize_motors(self, pins=[5, 6, 13, 19]):

        self._motors = []

        for i, pin in enumerate(pins):
            print(f"\tInitializing Motor {i} at pin:{pin}...")
            self._motors.append( Servo(pin, pin_factory=self._factory) )
        
        [self.set_motor_speed(i, 0) for i in range(4)]