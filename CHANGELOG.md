# 更新日志

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-03-14

### Added
- 初始版本发布
- 核心库 (claw):
  - 串口扫描功能
  - 机械爪连接与控制
  - 角度控制 (0-180°)
  - 配置管理
- CLI 命令行工具:
  - `scan` - 扫描串口
  - `connect` - 连接机械爪
  - `move` - 移动到指定角度
  - `open` - 打开爪
  - `close` - 关闭爪
  - `status` - 查看状态
  - `full-open` - 完全打开
  - `full-close` - 完全关闭
  - `grip` - 抓握位置
  - `reset` - 复位
- GUI 桌面应用 (PyQt6):
  - 串口扫描与连接
  - 角度滑块控制
  - 快捷操作按钮
  - 实时状态显示
  - 日志输出窗口
- GitHub Actions 自动构建
- 完整的文档和示例代码

### Changed
- None

### Deprecated
- None

### Removed
- None

### Fixed
- None

### Security
- None
