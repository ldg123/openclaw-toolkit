"""
OpenClaw Toolkit GUI 主窗口
"""

import sys
import threading
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QSlider, QTextEdit, QGroupBox,
    QMessageBox, QStatusBar, QMenuBar, QMenu
)
from PyQt6.QtCore import Qt, pyqtSignal, QObject, pyqtSlot
from PyQt6.QtGui import QAction, QIcon, QPalette, QColor

from claw import ClawController, scan_ports, get_port_info
from claw.config import get_config


class WorkerSignals(QObject):
    """工作线程信号"""
    finished = pyqtSignal()
    error = pyqtSignal(str)
    status_changed = pyqtSignal(dict)
    log_message = pyqtSignal(str)


class ClawWorker(threading.Thread):
    """机械爪控制工作线程"""
    
    def __init__(self, port: str, baudrate: int = 115200):
        super().__init__()
        self.port = port
        self.baudrate = baudrate
        self.controller = None
        self.running = True
        self.signals = WorkerSignals()
        self.daemon = True
        
    def run(self):
        """运行工作线程"""
        try:
            self.controller = ClawController(self.port, self.baudrate)
            
            if self.controller.connect():
                self.signals.status_changed.emit({
                    "connected": True,
                    "port": self.port,
                    "angle": self.controller.current_status.angle,
                    "gripper_open": self.controller.current_status.gripper_open
                })
                self.signals.log_message.emit(f"已连接到 {self.port}")
                
                # 保持连接并响应命令
                while self.running:
                    pass
                    
            else:
                self.signals.error.emit(f"连接失败: {self.controller.current_status.error}")
                
        except Exception as e:
            self.signals.error.emit(str(e))
        finally:
            if self.controller:
                self.controller.disconnect()
            self.signals.finished.emit()
            
    def stop(self):
        """停止工作线程"""
        self.running = False
        if self.controller:
            self.controller.disconnect()
            
    def move_angle(self, angle: int):
        """移动到指定角度"""
        if self.controller and self.controller.is_connected():
            self.controller.move_angle(angle)
            self.signals.status_changed.emit({
                "angle": angle
            })
            
    def open_gripper(self):
        """打开爪"""
        if self.controller and self.controller.is_connected():
            self.controller.open_gripper()
            self.signals.status_changed.emit({
                "gripper_open": True
            })
            self.signals.log_message.emit("爪已打开")
            
    def close_gripper(self):
        """关闭爪"""
        if self.controller and self.controller.is_connected():
            self.controller.close_gripper()
            self.signals.status_changed.emit({
                "gripper_open": False
            })
            self.signals.log_message.emit("爪已关闭")
            
    def full_open(self):
        """完全打开"""
        if self.controller and self.controller.is_connected():
            self.controller.full_open()
            self.signals.status_changed.emit({
                "angle": 180,
                "gripper_open": True
            })
            self.signals.log_message.emit("爪已完全打开 (180°)")
            
    def full_close(self):
        """完全关闭"""
        if self.controller and self.controller.is_connected():
            self.controller.full_close()
            self.signals.status_changed.emit({
                "angle": 0,
                "gripper_open": False
            })
            self.signals.log_message.emit("爪已完全关闭 (0°)")
            
    def grip(self):
        """抓握"""
        if self.controller and self.controller.is_connected():
            self.controller.grip()
            self.signals.status_changed.emit({
                "angle": 45,
                "gripper_open": False
            })
            self.signals.log_message.emit("已设置抓握位置 (45°)")
            
    def reset(self):
        """复位"""
        if self.controller and self.controller.is_connected():
            self.controller.reset()
            self.signals.status_changed.emit({
                "angle": 90,
                "gripper_open": True
            })
            self.signals.log_message.emit("已复位 (90°)")


class MainWindow(QMainWindow):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        self.worker = None
        self.config = get_config()
        self.log_lines = []
        self.max_log_lines = 1000
        
        self.init_ui()
        self.refresh_ports()
        
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("OpenClaw Toolkit - 机械爪控制")
        self.setGeometry(100, 100, 800, 600)
        
        # 创建菜单
        self.create_menu_bar()
        
        # 中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        layout = QVBoxLayout(central_widget)
        
        # 连接控制组
        connection_group = self.create_connection_group()
        layout.addWidget(connection_group)
        
        # 角度控制组
        angle_group = self.create_angle_group()
        layout.addWidget(angle_group)
        
        # 快捷操作组
        quick_group = self.create_quick_group()
        layout.addWidget(quick_group)
        
        # 日志显示
        log_group = self.create_log_group()
        layout.addWidget(log_group)
        
        # 状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("未连接")
        
    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu("文件")
        
        refresh_action = QAction("刷新串口", self)
        refresh_action.triggered.connect(self.refresh_ports)
        file_menu.addAction(refresh_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu("帮助")
        
        about_action = QAction("关于", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def create_connection_group(self) -> QGroupBox:
        """创建连接控制组"""
        group = QGroupBox("连接控制")
        layout = QHBoxLayout()
        
        # 串口选择
        layout.addWidget(QLabel("串口:"))
        self.port_combo = QComboBox()
        self.port_combo.setMinimumWidth(150)
        layout.addWidget(self.port_combo)
        
        # 刷新按钮
        refresh_btn = QPushButton("刷新")
        refresh_btn.clicked.connect(self.refresh_ports)
        layout.addWidget(refresh_btn)
        
        # 波特率
        layout.addWidget(QLabel("波特率:"))
        self.baudrate_combo = QComboBox()
        self.baudrate_combo.addItems(["9600", "19200", "38400", "57600", "115200", "230400", "460800", "921600"])
        self.baudrate_combo.setCurrentText("115200")
        self.baudrate_combo.setMinimumWidth(100)
        layout.addWidget(self.baudrate_combo)
        
        # 连接按钮
        self.connect_btn = QPushButton("连接")
        self.connect_btn.clicked.connect(self.toggle_connection)
        layout.addWidget(self.connect_btn)
        
        layout.addStretch()
        
        group.setLayout(layout)
        return group
        
    def create_angle_group(self) -> QGroupBox:
        """创建角度控制组"""
        group = QGroupBox("角度控制")
        layout = QVBoxLayout()
        
        # 角度显示
        angle_layout = QHBoxLayout()
        angle_layout.addWidget(QLabel("角度:"))
        self.angle_label = QLabel("90°")
        self.angle_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        angle_layout.addWidget(self.angle_label)
        angle_layout.addStretch()
        
        layout.addLayout(angle_layout)
        
        # 滑块
        self.angle_slider = QSlider(Qt.Orientation.Horizontal)
        self.angle_slider.setMinimum(0)
        self.angle_slider.setMaximum(180)
        self.angle_slider.setValue(90)
        self.angle_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.angle_slider.setTickInterval(30)
        self.angle_slider.valueChanged.connect(self.on_angle_changed)
        layout.addWidget(self.angle_slider)
        
        # 设置角度按钮
        btn_layout = QHBoxLayout()
        for angle in [0, 45, 90, 135, 180]:
            btn = QPushButton(f"{angle}°")
            btn.clicked.connect(lambda checked, a=angle: self.set_angle(a))
            btn_layout.addWidget(btn)
            
        layout.addLayout(btn_layout)
        
        group.setLayout(layout)
        return group
        
    def create_quick_group(self) -> QGroupBox:
        """创建快捷操作组"""
        group = QGroupBox("快捷操作")
        layout = QHBoxLayout()
        
        self.full_open_btn = QPushButton("全开")
        self.full_open_btn.clicked.connect(self.on_full_open)
        self.full_open_btn.setMinimumHeight(40)
        self.full_open_btn.setStyleSheet("background-color: #4CAF50; color: white; font-size: 14px;")
        layout.addWidget(self.full_open_btn)
        
        self.grip_btn = QPushButton("抓握")
        self.grip_btn.clicked.connect(self.on_grip)
        self.grip_btn.setMinimumHeight(40)
        self.grip_btn.setStyleSheet("background-color: #FF9800; color: white; font-size: 14px;")
        layout.addWidget(self.grip_btn)
        
        self.full_close_btn = QPushButton("全闭")
        self.full_close_btn.clicked.connect(self.on_full_close)
        self.full_close_btn.setMinimumHeight(40)
        self.full_close_btn.setStyleSheet("background-color: #f44336; color: white; font-size: 14px;")
        layout.addWidget(self.full_close_btn)
        
        self.reset_btn = QPushButton("复位")
        self.reset_btn.clicked.connect(self.on_reset)
        self.reset_btn.setMinimumHeight(40)
        layout.addWidget(self.reset_btn)
        
        layout.addStretch()
        
        group.setLayout(layout)
        return group
        
    def create_log_group(self) -> QGroupBox:
        """创建日志组"""
        group = QGroupBox("日志")
        layout = QVBoxLayout()
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150)
        layout.addWidget(self.log_text)
        
        # 清除日志按钮
        clear_btn = QPushButton("清除日志")
        clear_btn.clicked.connect(self.clear_log)
        layout.addWidget(clear_btn)
        
        group.setLayout(layout)
        return group
        
    def refresh_ports(self):
        """刷新串口列表"""
        self.port_combo.clear()
        
        ports = scan_ports()
        
        if ports:
            for port in ports:
                self.port_combo.addItem(port)
        else:
            self.port_combo.addItem("未找到串口")
            self.log_message("未找到可用串口")
            
    def toggle_connection(self):
        """切换连接状态"""
        if self.worker and self.worker.is_alive():
            self.disconnect()
        else:
            self.connect()
            
    def connect(self):
        """连接"""
        port = self.port_combo.currentText()
        
        if not port or port == "未找到串口":
            QMessageBox.warning(self, "警告", "请选择有效串口")
            return
            
        baudrate = int(self.baudrate_combo.currentText())
        
        self.log_message(f"正在连接 {port} @ {baudrate}bps...")
        self.connect_btn.setEnabled(False)
        
        self.worker = ClawWorker(port, baudrate)
        self.worker.signals.status_changed.connect(self.on_status_changed)
        self.worker.signals.log_message.connect(self.log_message)
        self.worker.signals.error.connect(self.on_connection_error)
        self.worker.start()
        
    def disconnect(self):
        """断开连接"""
        if self.worker:
            self.worker.stop()
            self.worker = None
            
        self.connect_btn.setText("连接")
        self.connect_btn.setEnabled(True)
        self.status_bar.showMessage("未连接")
        self.log_message("已断开连接")
        
    @pyqtSlot(dict)
    def on_status_changed(self, status: dict):
        """状态变化处理"""
        if status.get("connected"):
            self.connect_btn.setText("断开")
            self.connect_btn.setEnabled(True)
            self.status_bar.showMessage(f"已连接: {status.get('port')}")
            
        if "angle" in status:
            self.angle_label.setText(f"{status['angle']}°")
            if not self.angle_slider.isSliderDown():
                self.angle_slider.setValue(status['angle'])
                
    @pyqtSlot(str)
    def log_message(self, msg: str):
        """记录日志"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_lines.append(f"[{timestamp}] {msg}")
        
        if len(self.log_lines) > self.max_log_lines:
            self.log_lines = self.log_lines[-self.max_log_lines:]
            
        self.log_text.setPlainText("\n".join(self.log_lines))
        self.log_text.verticalScrollBar().setValue(self.log_text.verticalScrollBar().maximum())
        
    @pyqtSlot(str)
    def on_connection_error(self, error: str):
        """连接错误处理"""
        self.connect_btn.setText("连接")
        self.connect_btn.setEnabled(True)
        self.status_bar.showMessage("连接失败")
        QMessageBox.critical(self, "错误", error)
        
    def on_angle_changed(self, value: int):
        """角度变化处理"""
        self.angle_label.setText(f"{value}°")
        
        if self.worker and self.worker.is_alive():
            self.worker.move_angle(value)
            
    def set_angle(self, angle: int):
        """设置角度"""
        self.angle_slider.setValue(angle)
        
    def on_full_open(self):
        """全开"""
        if self.worker and self.worker.is_alive():
            self.worker.full_open()
            
    def on_full_close(self):
        """全闭"""
        if self.worker and self.worker.is_alive():
            self.worker.full_close()
            
    def on_grip(self):
        """抓握"""
        if self.worker and self.worker.is_alive():
            self.worker.grip()
            
    def on_reset(self):
        """复位"""
        if self.worker and self.worker.is_alive():
            self.worker.reset()
            
    def clear_log(self):
        """清除日志"""
        self.log_lines.clear()
        self.log_text.clear()
        
    def show_about(self):
        """显示关于对话框"""
        QMessageBox.about(
            self,
            "关于 OpenClaw Toolkit",
            "OpenClaw Toolkit v1.0.0\n\n"
            "开源机械爪 & 舵机控制工具箱\n\n"
            "支持 CLI + GUI 双模式\n\n"
            "MIT License"
        )
        
    def closeEvent(self, event):
        """关闭事件"""
        if self.worker:
            self.worker.stop()
        event.accept()


def main():
    """GUI 入口"""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # 设置主题色
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(240, 240, 240))
    app.setPalette(palette)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
