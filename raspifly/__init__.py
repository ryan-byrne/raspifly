from time import sleep, time
from threading import Thread
from gpiozero import DistanceSensor, Servo
from gpiozero.pins.pigpio import PiGPIOFactory
from gpiozero.pins.mock import MockFactory
import numpy as np
import math, random
import smbus2 as smbus

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

class BLHeli32():
    def __init__(self, pin, factory, max_thrust=6.66, ):

        print(f"\tInitializing BLHeli32 Controller at Pin:{pin}")

        self._max_thrust = max_thrust
        self._pwm = Servo(pin, pin_factory=factory)
        self.set(0)

    def set(self, value, unit="percent"):

        if unit == 'percent':
            self._pwm.value = value / 50 - 1
        elif unit == 'newtons':
            self._pwm.value = value / self._max_thrust / 50 - 1
        else:
            raise ValueError(f"The unit '{unit}' is invalid")

    def close(self):
        self._pwm.close()

class MPU6050():

    def __init__(self, address=0x68, channel=1, accelerometer_range=0, gyrometer_range=0, sample_rate=100, simulation_mode=False):

        self._sim_mode = simulation_mode

        print(f"Initializing MPU6050 at channel: {channel} and address: {address}...")

        # Setting I2C bus channel and address
        self._bus = smbus.SMBus(channel)
        self._ADDRESS = address

        # Setting Accelerometer and Gyroscope Ranges
        self._accel_range = ACCEL_FULL_SCALES[accelerometer_range]
        self._gyro_range = ACCEL_FULL_SCALES[gyrometer_range]

        # Setting initial telemetry values
        self.angles = [[0.0],[0.0],[0.0]]
        self.rates = [[0.0],[0.0],[0.0]]

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

        roll = -math.pi / 2 * math.sin( math.pi * self._read(ACCEL_X_HIGH)/ 32768) - self.ROLL_OFFSET
        pitch = -math.pi / 2 * math.sin( math.pi * self._read(ACCEL_Y_HIGH)/ 32768) - self.PITCH_OFFSET
        yaw = -math.pi / 2 * math.sin( math.pi * self._read(ACCEL_Z_HIGH)/ 32768) - self.YAW_OFFSET

        self.angles = [[roll],[pitch],[yaw]]

        roll_rate = 250/180 * math.pi * math.sin( math.pi * self._read(GYRO_Y_HIGH) / 32768) - self.ROLL_VEL_OFFSET
        pitch_rate = 250/180 * math.pi * math.sin( math.pi * self._read(GYRO_X_HIGH) / 32768) - self.PITCH_VEL_OFFSET
        yaw_rate = 250/180 * math.pi * math.sin( math.pi * self._read(GYRO_Z_HIGH) / 32768) - self.YAW_VEL_OFFSET

        self.rates = [[roll_rate],[pitch_rate],[yaw_rate]]

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
class SimMPU6050():

    def __init__(self):
        self.angles = [[0.0],[0.0],[0.0]]
        self.rates = [[0.0],[0.0],[0.0]]

    def close(self):
        pass

    def apply_thrusts(self, thrusts):
        
        t_0, t_1, t_2, t_3 = thrusts

        torques = [
            []
        ]


class SimMotor():

    def __init__(self, pin, max_thrust):
        
        print(f"\tInitializing Simulated Motor Controller at Pin:{pin} with Max Thrust={max_thrust}")
        self._max_thrust = max_thrust
        self.current_thrust = 0.0

    def set(self, speed):

        error = random.random() * 0.04 - 0.02
        target_thrust = speed / 100 * self._max_thrust
        self.current_thrust = target_thrust * ( 1 + error )

    def close(self):
        pass

class Raspifly():

    def __init__(
        self, mass=0.5, h=167, b=167, max_motor_thrust=6.66, layout='x', p_gain=4.0, i_gain=4.0, 
        d_gain=4.0, hz=40, us_echo_pin=23, us_trig_pin=24, motor_pins=[5, 6, 13, 19], simulation_mode=False
    ):

        """Class for Drone Control using Python     
        """

        self._max_motor_thrust = max_motor_thrust # Maximum Single Motor Thrust (N)
        self._hover_thrust = ( mass * 9.8 / 4 ) / max_motor_thrust * 100
        self._h ,self._b = h, b
        
        self._p_gain = p_gain # Proportional Gain
        self._i_gain = i_gain # Integral Gain
        self._d_gain = d_gain # Derivative Gain
        self._prev_error = [[0.0],[0.0],[0.0]]
        self._prev_time = time()

        self._read_rate = 1/hz # Rate to send commands to the motors
        self.active = False # Control Loop Active

        self._sim_mode = simulation_mode

        if simulation_mode:
            self.accelerometer = SimMPU6050()
            self.ultrasonic_sensor = DistanceSensor(us_echo_pin, us_trig_pin, max_distance=5.0, pin_factory=MockFactory())
            self.motors = [SimMotor(pin, max_thrust=6.66) for pin in motor_pins]
        else:
            self.accelerometer = MPU6050()
            self.ultrasonic_sensor = DistanceSensor(us_echo_pin, us_trig_pin, max_distance=5.0, pin_factory=PiGPIOFactory())
            self.motors = [BLHeli32(pin, max_thrust=6.66, factory=PiGPIOFactory()) for pin in motor_pins]
    
    def start(self):
        
        print("Starting Raspifly...")
        
        self.active = True

        Thread(target=self._main_control_loop).start()

    def stop(self):

        self.active = False

        print("Shutting down Raspifly...")

        print("Closing Motors")
        [m.close() for m in self.motors]

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

        # Actual Roll, Pitch and Yaw Velocities
        actual = self.accelerometer.rates

        # Calculate Error
        error = np.subtract( target, actual )

        # Calculate Change in Time
        dt = time() - self._prev_time

        # Proportional Controller
        p_control = self._p_gain * error

        # Integral Controller
        #i_control = self._i_gain * np.subtract( error, self._prev_error ) * dt

        # Derivative Controller
        #d_control = self._d_gain * np.subtract( error, self._prev_error ) / dt

        # Store the output command
        output = p_control

        """
        
        X-Configuration
           1  0
            \/
            /\ 
           2  3 

        roll = ( 3 + 0 ) - ( 2 + 1 )
        pitch = ( 1 + 0 ) - ( 2 + 3 )

        t-Configuration
            0
            |
        1 -- -- 3
            |
            2

        """

        moments_of_inertia = [
            [ self._b*self._h**3/12 , 0 , 0 ],
            [ 0 , self._h*self._b**3/12, 0 ],
            [ 0 , 0 , 0 ]
        ]

        motor_speeds = [10.0, 10.0, 10.0, 10.0]

        [self.motors[i].set(speed) for i, speed in enumerate(motor_speeds)]

        if self._sim_mode:
            self.accelerometer.apply_thrusts([m.current_thrust for m in self.motors])

        self._prev_time = time()

    def calibrate_motors(self):

        input("Plug in the Raspberry Pi, power down the motors, then Press Enter to Begin Motor Calibration")

        print("Setting Maximum Throttle...")

        for motor in self.motors:
            motor.set( 100 )

        input("Power on your ESCs. Press Enter after Beeping stops")

        print("Setting Minimum Calibration")

        for motor in self.motors:
            motor.set( 0 )

        input("Press Enter after beeping stops.")

        print("Motor calibration complete")

        