"""
OpenClaw Toolkit GUI 入口
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gui.window import main

if __name__ == '__main__':
    main()
