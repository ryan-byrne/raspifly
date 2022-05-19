import time
from raspifly import Raspifly

drone = Raspifly()

drone.start()

input("Get Moving")

[drone.set_motor_speed(motor=i, percent_speed=30) for i in range(4)]

input("Press Enter to Stop")

drone.stop()