import serial


class Arm_Device:
    def __init__(self, port: str = '/dev/ttyUSB0', baudrate: int = 9600, timeout: float = 1.0):
        self.ser = serial.Serial(port, baudrate, timeout=timeout)
        self.frame_header = b'\x55\x55'
        # 逻辑ID(应用中的 1~6 顺序) -> 物理ID(实际硬件接线顺序)
        # 逻辑: 1-基座,2-肩,3-肘,4-腕俯仰,5-腕旋转,6-夹爪
        # 物理: 6-基座,5-肩,4-肘,3-腕俯仰,2-腕旋转,1-夹爪
        self.id_map = {1: 6, 2: 5, 3: 4, 4: 3, 5: 2, 6: 1}
        # 统一映射：将“机械角度(度)”线性映射到协议要求的位置值 0~1000
        # 协议中 0~1000 对应 0~240°。为保持与项目脚本一致：
        # - 物理ID 2（腕旋转）按 0~270° 映射到 0~1000；其余关节按 0~180° 映射到 0~1000
        # - 需要反向的关节在这里显式处理
        self.deg_limits = {1: 180, 2: 270, 3: 180, 4: 180, 5: 180, 6: 180}
        self.invert_ids = {2, 4}

    def _degree_to_value(self, servo_id: int, angle_deg: float) -> int:
        # 根据关节最大角度做线性缩放，并按需要做方向反转
        deg_max = self.deg_limits.get(servo_id, 180)
        if servo_id in self.invert_ids:
            angle_deg = deg_max - angle_deg
        # 裁剪到合法范围
        if angle_deg < 0:
            angle_deg = 0
        elif angle_deg > deg_max:
            angle_deg = deg_max
        # 映射到 0~1000（协议的角度值）
        angle_value = int(round(angle_deg / deg_max * 1000))
        # 最终再裁剪一次，保证安全
        if angle_value < 0:
            return 0
        if angle_value > 1000:
            return 1000
        return angle_value

    def _send(self, cmd: int, params: bytes):
        length = len(params) + 2
        if length > 255:
            raise ValueError(f"参数过长，长度 {length} 超过255")
        frame = self.frame_header + length.to_bytes(1, 'big') + cmd.to_bytes(1, 'big') + params
        self.ser.reset_input_buffer()
        self.ser.write(frame)

    def Arm_serial_servo_write(self, servo_id: int, angle_deg: float, time_ms: int):
        hw_id = self.id_map.get(servo_id, servo_id)
        angle_value = self._degree_to_value(hw_id, angle_deg)
        time_low = time_ms & 0xFF
        time_high = (time_ms >> 8) & 0xFF
        angle_low = angle_value & 0xFF
        angle_high = (angle_value >> 8) & 0xFF
        params = (
            b'\x01'  # 舵机个数
            + time_low.to_bytes(1, 'big')
            + time_high.to_bytes(1, 'big')
            + hw_id.to_bytes(1, 'big')
            + angle_low.to_bytes(1, 'big')
            + angle_high.to_bytes(1, 'big')
        )
        self._send(3, params)
        return True

    def Arm_serial_servo_write6_array(self, angles_deg, time_ms: int):
        if len(angles_deg) != 6:
            raise ValueError('angles_deg 需要 6 个元素')
        time_low = time_ms & 0xFF
        time_high = (time_ms >> 8) & 0xFF
        params = b'\x06' + time_low.to_bytes(1, 'big') + time_high.to_bytes(1, 'big')
        for servo_id, ang in enumerate(angles_deg, start=1):
            hw_id = self.id_map.get(servo_id, servo_id)
            angle_value = self._degree_to_value(hw_id, ang)
            angle_low = angle_value & 0xFF
            angle_high = (angle_value >> 8) & 0xFF
            params += hw_id.to_bytes(1, 'big') + angle_low.to_bytes(1, 'big') + angle_high.to_bytes(1, 'big')
        self._send(3, params)
        return True

    def Arm_serial_servo_write6(self, s1, s2, s3, s4, s5, s6, time):
        return self.Arm_serial_servo_write6_array([s1, s2, s3, s4, s5, s6], time)

    def Arm_Buzzer_On(self, delay=0xFF):
        # 无蜂鸣器，安全空实现
        return True

    def close(self):
        try:
            self.ser.close()
        except Exception:
            pass