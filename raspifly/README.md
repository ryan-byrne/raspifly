# Raspifly Python Package

## Inputs

### Accelerometer

* X-Acceleration
* Y-Acceleration
* Z-Acceleration
* 
### Ultrasonic Sensor

* Z-Position
### Positions in the Inertial Frame
```python
# X and Y are unknown, but Z is found with US Sensor
linear_position = [ [x_pos], [y_pos], [z_pos] ]
# Taken from the Gyroscope
angular_position = [ [roll], [pitch], [yaw] ]
# Vector containing both
q = [ [linear_position], [angular_position] ]
```

### Velocities in the Body Frame
```python
# No way to measure?
linear_velocity_body = [ [vel_x], [vel_y], [vel_z] ]
# Measured by Gyroscope
angular_velovity_body = [ [p], [q], [r] ]
```

### Rotation Matrix