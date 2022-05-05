from time import sleep
from raspifly import MPU6050

accel = MPU6050()

while True:
    print(accel.read())
    sleep(1)