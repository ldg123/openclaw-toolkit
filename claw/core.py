"""
机械爪控制器核心类
"""

import serial
import serial.tools.list_ports
import time
import json
import os
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, asdict


@dataclass
class ClawStatus:
    """机械爪状态"""
    connected: bool = False
    port: str = ""
    baudrate: int = 115200
    angle: int = 90
    gripper_open: bool = True
    firmware_version: str = ""
    error: str = ""


class ClawController:
    """机械爪控制器"""
    
    # 指令常量
    CMD_SCAN = b"SCAN\r\n"
    CMD_OPEN = b"OPEN\r\n"
    CMD_CLOSE = b"CLOSE\r\n"
    CMD_MOVE = b"MOVE:{}\r\n"
    CMD_STATUS = b"STATUS\r\n"
    CMD_RESET = b"RESET\r\n"
    
    # 角度范围
    ANGLE_MIN = 0
    ANGLE_MAX = 180
    ANGLE_DEFAULT = 90
    
    def __init__(self, port: str = "", baudrate: int = 115200, timeout: float = 1.0):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial_conn: Optional[serial.Serial] = None
        self._status = ClawStatus()
        
    def connect(self, port: Optional[str] = None) -> bool:
        """连接机械爪"""
        if port:
            self.port = port
            
        if not self.port:
            return False
            
        try:
            self.serial_conn = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE
            )
            time.sleep(0.5)  # 等待连接稳定
            
            self._status.connected = True
            self._status.port = self.port
            self._status.baudrate = self.baudrate
            
            # 获取状态
            self.status()
            return True
            
        except serial.SerialException as e:
            self._status.error = str(e)
            return False
    
    def disconnect(self) -> None:
        """断开连接"""
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
        self._status.connected = False
        
    def is_connected(self) -> bool:
        """检查连接状态"""
        return self._status.connected
    
    def send_command(self, cmd: bytes) -> str:
        """发送指令并读取响应"""
        if not self.serial_conn or not self.serial_conn.is_open:
            return ""
        
        self.serial_conn.flushInput()
        self.serial_conn.write(cmd)
        time.sleep(0.1)
        
        response = b""
        while self.serial_conn.in_waiting > 0:
            response += self.serial_conn.read(self.serial_conn.in_waiting)
            time.sleep(0.05)
            
        return response.decode('utf-8', errors='ignore').strip()
    
    def open_gripper(self) -> bool:
        """打开爪"""
        response = self.send_command(self.CMD_OPEN)
        if "OK" in response or not response:
            self._status.gripper_open = True
            return True
        return False
    
    def close_gripper(self) -> bool:
        """关闭爪"""
        response = self.send_command(self.CMD_CLOSE)
        if "OK" in response or not response:
            self._status.gripper_open = False
            return True
        return False
    
    def move_angle(self, angle: int) -> bool:
        """移动到指定角度"""
        if not self.ANGLE_MIN <= angle <= self.ANGLE_MAX:
            self._status.error = f"角度必须在 {self.ANGLE_MIN}-{self.ANGLE_MAX} 之间"
            return False
            
        cmd = self.CMD_MOVE.format(angle).encode('utf-8')
        response = self.send_command(cmd)
        
        if "OK" in response or not response:
            self._status.angle = angle
            return True
        return False
    
    def full_open(self) -> bool:
        """完全打开"""
        return self.move_angle(self.ANGLE_MAX)
    
    def full_close(self) -> bool:
        """完全关闭"""
        return self.move_angle(self.ANGLE_MIN)
    
    def grip(self) -> bool:
        """抓握位置（45度）"""
        return self.move_angle(45)
    
    def reset(self) -> bool:
        """复位"""
        response = self.send_command(self.CMD_RESET)
        if "OK" in response or not response:
            self._status.angle = self.ANGLE_DEFAULT
            self._status.gripper_open = True
            return True
        return False
    
    def status(self) -> ClawStatus:
        """获取状态"""
        response = self.send_command(self.CMD_STATUS)
        
        # 模拟解析响应（实际根据设备固件调整）
        if "ANGLE" in response:
            try:
                angle = int(response.split("ANGLE")[1].split()[0])
                self._status.angle = angle
            except:
                pass
                
        if "GRIPPER" in response:
            self._status.gripper_open = "OPEN" in response
            
        return self._status
    
    @property
    def current_status(self) -> ClawStatus:
        """获取当前状态"""
        return self._status
    
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
