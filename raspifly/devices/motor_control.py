from gpiozero import Servo
import random

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