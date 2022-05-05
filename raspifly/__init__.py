from time import sleep
from threading import Thread
from gpiozero import DistanceSensor, Servo, Device
from gpiozero.pins.pigpio import PiGPIOFactory
import smbus

DEFAULT_TELEMETRY_FIELDS = [
    'x_pos','y_pos','z_pos',
    'x_vel','y_vel','z_vel',
    'x_acc','y_acc','z_acc',
    'roll','pitch','yaw',
    'roll_vel','pitch_vel','yaw_vel',
    'roll_acc','pitch_acc','yaw_acc',
]
"""
Wire.begin();                    
Wire.beginTransmission(MPU);   
Wire.write(0x6B);               
Wire.write(0x00);             
Wire.endTransmission(true);    
calculate_IMU_error();
delay(20);

Wire.beginTransmission(MPU);
Wire.write(0x3B); 
Wire.endTransmission(false);
Wire.requestFrom(MPU, 6, true);
AccX = (Wire.read() << 8 | Wire.read()) / 16384.0;
AccY = (Wire.read() << 8 | Wire.read()) / 16384.0;
AccZ = (Wire.read() << 8 | Wire.read()) / 16384.0;
accAngleX = (atan(AccY / sqrt(pow(AccX, 2) + pow(AccZ, 2))) * 180 / PI) - 0.58; 
accAngleY = (atan(-1 * AccX / sqrt(pow(AccY, 2) + pow(AccZ, 2))) * 180 / PI) + 1.58; 
previousTime = currentTime;       
currentTime = millis(); 
elapsedTime = (currentTime - previousTime) / 1000; 
Wire.beginTransmission(MPU);
Wire.write(0x43);
Wire.endTransmission(false);
Wire.requestFrom(MPU, 6, true); 
GyroX = (Wire.read() << 8 | Wire.read()) / 131.0; 
GyroY = (Wire.read() << 8 | Wire.read()) / 131.0;
GyroZ = (Wire.read() << 8 | Wire.read()) / 131.0;
GyroX = GyroX + 0.56; 
GyroY = GyroY - 2;
GyroZ = GyroZ + 0.79; 
gyroAngleX = gyroAngleX + GyroX * elapsedTime;
gyroAngleY = gyroAngleY + GyroY * elapsedTime;
yaw =  yaw + GyroZ * elapsedTime;
roll = 0.96 * gyroAngleX + 0.04 * accAngleX;
pitch = 0.96 * gyroAngleY + 0.04 * accAngleY;
"""

class MPU6050():

    def __init__(self, address=0x60, channel=1):

        self._bus = smbus.SMBus(channel)
        self._ADDRESS = address
        # Useful Bytes
        
        # Startup
        self._bus.write_byte(self._ADDRESS, 0x6B)
        self._bus.write_byte(self._ADDRESS, 0x00)

        self.acc_x = 0
        self.acc_y = 0
        self.acc_z = 0
        self.gyro_x = 0
        self.gyro_y = 0
        self.gyro_z = 0


    def _update(self):
        self._bus.write_byte(self._address, 0x3B)

        pass

    def close(self):
        pass

class Raspifly():

    def __init__(self):

        """Class for Drone Control using Python     
        """
        # Set initial value of 0 for each telemetry field
        [setattr(self, field, 0) for field in DEFAULT_TELEMETRY_FIELDS]
        # Set Pin Factory
        self._factory = PiGPIOFactory()
        self.active = False
    
    def start(
            self,
            front_right_motor_pin=5,
            front_left_motor_pin=6,
            back_right_motor_pin=13,
            back_left_motor_pin=19,
            ultrasonic_echo_pin=23,  
            ultrasonic_trig_pin=24
    ):
        print("Starting Raspifly...")
        # Initialize Inputs
        self._initialize_inputs(ultrasonic_echo_pin, ultrasonic_trig_pin, accelerometer_scl_pin, accelerometer_sda_pin)
        # Initialize Motors
        self._initialize_motors(front_right_motor_pin, front_left_motor_pin, back_right_motor_pin, back_left_motor_pin)
        
        self.active = True

        Thread(target=self._main_control_loop).start()

    def stop(self):
        self.active = False
        print("Shutting down Raspifly...")
        for _device in ['_front_right','_front_left','_back_left','_back_right','_accelerometer','_ultrasonic_sensor']:
            print(f"\tClosing {_device}")
            getattr(self, _device).close()

    def _main_control_loop(self):
        while self.active:
            self._update_telemetry()
            sleep(0.1)

    def _initialize_inputs(self, _echo, _trig, _scl, _sda):

        print("Initializing Inputs...")

        print(f"\tInitializing Ultrasonic Sensor with Echo={_echo} and Trig={_trig}")
        self._ultrasonic_sensor = DistanceSensor(_echo, _trig, max_distance=5.0, pin_factory=self._factory)

        print(f"\tInitializing Accelerometer on the I2C Bus")
        self._accelerometer = MPU6050()


    def _initialize_motors(self, *pins):

        print("Initializing Motors...")
        
        for i, _motor in enumerate(['_front_right','_front_left','_back_left','_back_right']):
            print(f"\tInitializing {_motor} at pin: {pins[i]}")
            setattr(self, _motor, Servo(pins[i], pin_factory=self._factory))


    def _update_telemetry(self):
        self.z_pos = self._ultrasonic_sensor.distance