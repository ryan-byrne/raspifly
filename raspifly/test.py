from time import sleep
from gpiozero import DistanceSensor

sensor = DistanceSensor(23, 24, max_distance=5.0)

while True:
    print('Distance to nearest object is', sensor.distance, 'm')
    sleep(0.1)