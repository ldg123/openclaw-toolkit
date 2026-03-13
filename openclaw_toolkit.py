#!/usr/bin/env python3
"""
OpenClaw Toolkit - 开源机械爪 & 舵机控制工具箱

用法:
    openclaw-toolkit gui     # 启动 GUI
    openclaw-toolkit scan   # 扫描串口
    openclaw-toolkit open   # 打开爪
    openclaw-toolkit close  # 关闭爪
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    """主入口"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="OpenClaw Toolkit - 开源机械爪 & 舵机控制工具箱"
    )
    
    parser.add_argument(
        "mode",
        choices=["gui", "cli"],
        nargs="?",
        default="gui",
        help="运行模式: gui 或 cli (默认: gui)"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="OpenClaw Toolkit v1.0.0"
    )
    
    args = parser.parse_args()
    
    if args.mode == "gui":
        from gui.window import main as gui_main
        gui_main()
    else:
        from cli.main import main as cli_main
        cli_main()


if __name__ == "__main__":
    main()
