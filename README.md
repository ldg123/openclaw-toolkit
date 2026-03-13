# OpenClaw Toolkit

<p align="center">
  <img src="assets/logo.png" alt="OpenClaw Toolkit Logo" width="200"/>
</p>

<p align="center">
  <a href="https://pypi.org/project/openclaw-toolkit/">
    <img src="https://img.shields.io/pypi/v/openclaw-toolkit.svg" alt="PyPI Version"/>
  </a>
  <a href="https://pypi.org/project/openclaw-toolkit/">
    <img src="https://img.shields.io/pypi/pyversions/openclaw-toolkit.svg" alt="Python Versions"/>
  </a>
  <a href="https://github.com/openclaw/openclaw-toolkit/actions">
    <img src="https://img.shields.io/github/actions/workflow/status/openclaw/openclaw-toolkit/build.yml" alt="Build Status"/>
  </a>
  <a href="LICENSE">
    <img src="https://img.shields.io/pypi/l/openclaw-toolkit.svg" alt="License"/>
  </a>
  <a href="https://github.com/openclaw/openclaw-toolkit/releases">
    <img src="https://img.shields.io/github/downloads/openclaw/openclaw-toolkit/total.svg" alt="Downloads"/>
  </a>
</p>

> 开源机械爪 & 舵机控制工具箱 | 支持 CLI + GUI 双模式

## 📋 简介

OpenClaw Toolkit 是一个功能强大的开源机械爪和舵机控制工具箱，提供命令行界面 (CLI) 和图形用户界面 (GUI) 两种使用方式，适用于开发者、爱好者和教育场景。

### ✨ 特性

- 🔌 **串口扫描** - 自动检测可用串口
- 🎮 **多模式控制** - CLI 和 GUI 双模式
- 🎯 **精确角度控制** - 0-180° 精确调节
- ⚡ **快捷操作** - 全开、全闭、抓握一键操作
- 🖥️ **跨平台** - Windows、Linux、macOS
- 🔧 **易于扩展** - 模块化设计
- 📦 **一键打包** - 自动构建可执行文件

## 🖥️ GUI 界面

<p align="center">
  <img src="screenshots/gui-main.png" alt="GUI Main Window" width="800"/>
</p>

### GUI 功能

- 串口自动扫描与连接
- 角度滑块精细控制
- 全开/全闭/抓握快捷按钮
- 实时状态显示
- 日志输出窗口
- 美观简洁的界面设计

## 🚀 快速开始

### 安装

#### 从 PyPI 安装 (推荐)

```bash
pip install openclaw-toolkit
```

#### 从源码安装

```bash
git clone https://github.com/openclaw/openclaw-toolkit.git
cd openclaw-toolkit
pip install -e .
```

### 安装 GUI 依赖 (可选)

```bash
pip install openclaw-toolkit[gui]
```

或者安装所有依赖:

```bash
pip install -e ".[dev]"
```

## 📖 使用方法

### GUI 模式

```bash
openclaw-toolkit gui
# 或者
openclaw-gui
```

### CLI 模式

#### 扫描串口

```bash
openclaw-toolkit scan
# 或者
openclaw-cli scan
```

输出示例:
```
正在扫描串口...

找到 3 个可用串口:

  - COM3
  - COM4
  - COM5
```

#### 连接机械爪

```bash
openclaw-cli connect COM3
```

#### 查看状态

```bash
openclaw-cli status COM3
```

输出:
```
=== 机械爪状态 ===
  串口: COM3
  波特率: 115200
  当前角度: 90°
  爪状态: 打开
  连接: 已连接
```

#### 移动到指定角度

```bash
openclaw-cli move COM3 45
```

#### 打开爪

```bash
openclaw-cli open COM3
```

#### 关闭爪

```bash
openclaw-cli close COM3
```

#### 完全打开 (180°)

```bash
openclaw-cli full-open COM3
```

#### 完全关闭 (0°)

```bash
openclaw-cli full-close COM3
```

#### 抓握位置 (45°)

```bash
openclaw-cli grip COM3
```

#### 复位

```bash
openclaw-cli reset COM3
```

## 📁 项目结构

```
openclaw-toolkit/
├── claw/                 # 核心库
│   ├── __init__.py
│   ├── core.py          # 控制器核心类
│   ├── serial_utils.py  # 串口工具
│   └── config.py        # 配置管理
├── cli/                  # CLI 模块
│   ├── __init__.py
│   └── main.py          # CLI 主程序
├── gui/                  # GUI 模块
│   ├── __init__.py
│   ├── __main__.py
│   └── window.py       # PyQt6 主窗口
├── examples/             # 示例代码
│   └── basic_control.py
├── assets/               # 资源文件
├── screenshots/         # 截图
├── README.md            # 项目文档
├── LICENSE              # MIT 许可证
├── requirements.txt    # Python 依赖
├── setup.py            # 安装配置
└── pyproject.toml      # 项目配置
```

## 🔧 开发

### 运行测试

```bash
pytest
```

### 代码格式化

```bash
black .
```

### 类型检查

```bash
mypy .
```

### 构建发布包

```bash
python setup.py sdist bdist_wheel
```

## 🤝 贡献指南

欢迎贡献代码! 请阅读我们的 [贡献指南](CONTRIBUTING.md) 了解如何参与项目。

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 📝 更新日志

查看 [CHANGELOG.md](CHANGELOG.md) 了解每个版本的详细更改。

## 📄 许可证

本项目采用 [MIT](LICENSE) 许可证。

## 🔗 相关链接

- [文档](https://github.com/openclaw/openclaw-toolkit#readme)
- [问题反馈](https://github.com/openclaw/openclaw-toolkit/issues)
- [发布页面](https://github.com/openclaw/openclaw-toolkit/releases)

---

<p align="center">
  用 ❤️ 制作 by <a href="https://openclaw.ai">OpenClaw Team</a>
</p>
