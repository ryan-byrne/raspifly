import time
from gpiozero import DistanceSensor, Servo
from gpiozero.pins.pigpio import PiGPIOFactory
from raspifly import MPU6050

ECHO_PIN = 23
TRIG_PIN = 24

FR_PIN = 5
FL_PIN = 6
BR_PIN = 13
BL_PIN = 19

accelerometer = MPU6050()

while True:
    try:
        print("roll: ", accelerometer.roll_vel)
        print("pitch: ", accelerometer.pitch_vel)
        print()
    except KeyboardInterrupt:
        accelerometer.close()
        break
    time.sleep(0.1)