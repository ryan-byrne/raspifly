from time import sleep, time
from threading import Thread
import numpy as np
from gpiozero.pins.pigpio import PiGPIOFactory
from gpiozero.pins.mock import MockFactory
from .measurement import SimMPU6050, MPU6050, DistanceSensor
from .motor_control import SimMotor, BLHeli32

class Drone():

    def __init__(self):

        """Class for Drone Control using Python     
        """

        pass
    
    def start(self, mass=0.5, h=167, b=167, max_motor_thrust=6.66, layout='x', p_gain=4.0, i_gain=4.0, 
        d_gain=4.0, hz=40, us_echo_pin=23, us_trig_pin=24, motor_pins=[5, 6, 13, 19], simulation_mode=False):
        
        print("Starting Raspifly...")

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

    def status(self):
        # TODO
        return {"this":"is a status"}