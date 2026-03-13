"""
OpenClaw Toolkit - 开源机械爪 & 舵机控制工具箱
"""

__version__ = "1.0.0"
__author__ = "OpenClaw Team"
__license__ = "MIT"

from claw.core import ClawController
from claw.serial_utils import scan_ports, get_port_info

__all__ = [
    "ClawController",
    "scan_ports", 
    "get_port_info",
    "__version__",
]
