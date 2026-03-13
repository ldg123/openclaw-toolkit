"""
串口工具函数
"""

import serial
import serial.tools.list_ports
from typing import List, Dict, Optional, Any
import os


def scan_ports() -> List[str]:
    """
    扫描可用串口
    
    Returns:
        可用串口列表
    """
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]


def get_port_info() -> List[Dict[str, Any]]:
    """
    获取所有串口的详细信息
    
    Returns:
        串口信息列表
    """
    ports = serial.tools.list_ports.comports()
    result = []
    
    for port in ports:
        result.append({
            "device": port.device,
            "name": port.name or "",
            "description": port.description or "",
            "hwid": port.hwid or "",
            "vid": port.vid,
            "pid": port.pid,
            "serial_number": port.serial_number or "",
            "location": port.location or "",
            "manufacturer": port.manufacturer or "",
            "product": port.product or "",
            "interface": port.interface or "",
        })
    
    return result


def get_port_by_description(description: str) -> Optional[str]:
    """
    根据描述查找串口
    
    Args:
        description: 串口描述关键词
        
    Returns:
        串口设备路径，未找到返回 None
    """
    ports = serial.tools.list_ports.comports()
    
    for port in ports:
        if description.lower() in (port.description or "").lower():
            return port.device
            
    return None


def get_common_ports() -> List[str]:
    """
    获取常见舵机控制器串口
    
    Returns:
        常见串口列表
    """
    common = []
    ports = scan_ports()
    
    keywords = [
        "arduino", "ch340", "ch341", "cp210", "cp2102", 
        "ftdi", "uart", "servo", "claw", "robot",
        "usb", "serial"
    ]
    
    for port in ports:
        info = get_port_info()
        for p in info:
            if p["device"] == port:
                desc = p["description"].lower()
                manufacturer = p["manufacturer"].lower()
                
                if any(k in desc or k in manufacturer for k in keywords):
                    common.append(port)
                    break
                    
    return common


def test_port(port: str, baudrate: int = 115200, timeout: float = 0.5) -> bool:
    """
    测试串口是否可访问
    
    Args:
        port: 串口路径
        baudrate: 波特率
        timeout: 超时时间
        
    Returns:
        是否可访问
    """
    try:
        with serial.Serial(port, baudrate, timeout=timeout) as ser:
            return ser.is_open
    except:
        return False


def format_port_list(ports: List[Dict[str, Any]]) -> str:
    """
    格式化串口列表为字符串
    
    Args:
        ports: 串口信息列表
        
    Returns:
        格式化的字符串
    """
    if not ports:
        return "未找到可用串口"
        
    lines = ["可用串口:", "-" * 50]
    
    for i, port in enumerate(ports, 1):
        lines.append(f"{i}. {port['device']}")
        if port['description']:
            lines.append(f"   描述: {port['description']}")
        if port['manufacturer']:
            lines.append(f"   制造商: {port['manufacturer']}")
        if port['serial_number']:
            lines.append(f"   序列号: {port['serial_number']}")
        lines.append("")
        
    return "\n".join(lines)
