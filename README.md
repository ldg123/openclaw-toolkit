# OpenClaw Toolkit

[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8%2B-brightgreen)](https://python.org)

开源机械爪 & 舵机控制工具箱（CLI + GUI 双模式）

## 功能
- 串口自动扫描
- 舵机角度 / 机械爪开合百分比控制
- 全开、全闭快捷操作
- CLI 命令行模式
- GUI 图形界面（PyQt6）
- 跨平台：Windows / Linux / macOS / Raspberry Pi
- 自动打包为可执行文件

## 快速使用

### GUI
```bash
python gui/main.py
```

### CLI
```bash
python cli/main.py scan
python cli/main.py connect COM5
python cli/main.py move 90
python cli/main.py open
python cli/main.py close
```

## 技术栈

- Python 3.8+
- PyQt6
- pyserial
- click
