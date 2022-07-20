import smbus2, math, time
from threading import Thread
from gpiozero import DistanceSensor

class MPU6050():

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

    def __init__(self, address=0x68, channel=1, accelerometer_range=0, gyrometer_range=0, sample_rate=100, simulation_mode=False):

        self._sim_mode = simulation_mode

        print(f"Initializing MPU6050 at channel: {channel} and address: {address}...")

        # Setting I2C bus channel and address
        self._bus = smbus2.SMBus(channel)
        self._ADDRESS = address

        # Setting Accelerometer and Gyroscope Ranges
        self._accel_range = self.ACCEL_FULL_SCALES[accelerometer_range]
        self._gyro_range = self.ACCEL_FULL_SCALES[gyrometer_range]

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
            self._write(self.PWR_MGT_1, 1)
            self._write(self.CONFIG, 0)
            self._write(self.SAMPLE_RATE, 7)
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

        _roll, _pitch, _yaw, _roll_rate, _pitch_rate, _yaw_rate = [], [], [], [], [], []

        def _average(list):
            return sum(list) / len(list)

        for i in range(100):
            self._update_values()
            [roll], [pitch], [yaw] = self.angles
            _roll.append(roll)
            _pitch.append(pitch)
            _yaw.append(yaw)
            [roll_rate], [pitch_rate], [yaw_rate] = self.rates
            _roll_rate.append(roll_rate)
            _pitch_rate.append(pitch_rate)
            _yaw_rate.append(yaw_rate)

        self.ROLL_OFFSET = _average(_roll)
        self.PITCH_OFFSET = _average(_pitch)
        self.YAW_OFFSET = _average(_yaw)
        self.ROLL_VEL_OFFSET = _average(_roll_rate)
        self.PITCH_VEL_OFFSET = _average(_pitch_rate)
        self.YAW_VEL_OFFSET = _average(_yaw_rate)

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

        roll = -math.pi / 2 * math.sin( math.pi * self._read(self.ACCEL_X_HIGH)/ 32768) - self.ROLL_OFFSET
        pitch = -math.pi / 2 * math.sin( math.pi * self._read(self.ACCEL_Y_HIGH)/ 32768) - self.PITCH_OFFSET
        yaw = -math.pi / 2 * math.sin( math.pi * self._read(self.ACCEL_Z_HIGH)/ 32768) - self.YAW_OFFSET

        self.angles = [[roll],[pitch],[yaw]]

        roll_rate = 250/180 * math.pi * math.sin( math.pi * self._read(self.GYRO_Y_HIGH) / 32768) - self.ROLL_VEL_OFFSET
        pitch_rate = 250/180 * math.pi * math.sin( math.pi * self._read(self.GYRO_X_HIGH) / 32768) - self.PITCH_VEL_OFFSET
        yaw_rate = 250/180 * math.pi * math.sin( math.pi * self._read(self.GYRO_Z_HIGH) / 32768) - self.YAW_VEL_OFFSET

        self.rates = [[roll_rate],[pitch_rate],[yaw_rate]]

        time.sleep(1/self._sample_rate)
    
    def _write(self, addr, cmd):
        self._bus.write_byte_data(self._ADDRESS, addr, cmd)

    def _read(self, addr):
        return (self._bus.read_byte_data(self._ADDRESS, addr)<<8)|self._bus.read_byte_data(self._ADDRESS, addr+1)

    def _update(self):
        pass

    def close(self):
        self.active = False
        self._write(self.PWR_MGT_1, 0)

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