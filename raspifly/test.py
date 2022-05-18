import time
from raspifly import Raspifly

drone = Raspifly()

drone.start()

input("Get Moving")

drone.set_motor_speed(motor=0, percent_speed=30)

input("Press Enter to Stop")

drone.stop()