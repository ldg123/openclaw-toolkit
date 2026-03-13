# -*- coding: utf-8 -*-
"""
OpenClaw Toolkit GUI Main Window - Beautified Version
"""

import sys
import threading
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QSlider, QTextEdit, QGroupBox,
    QMessageBox, QStatusBar, QMenuBar, QMenu, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal, QObject, pyqtSlot, QSize
from PyQt6.QtGui import QAction, QIcon, QPalette, QColor, QLinearGradient, QFont, QPainter

from claw import ClawController, scan_ports, get_port_info
from claw.config import get_config


# Modern color scheme
COLORS = {
    'primary': '#6366F1',
    'primary_dark': '#4F46E5',
    'secondary': '#10B981',
    'danger': '#EF4444',
    'warning': '#F59E0B',
    'dark': '#1F2937',
    'light': '#F9FAFB',
    'white': '#FFFFFF',
    'gray': '#6B7280',
    'bg_gradient_start': '#667EEA',
    'bg_gradient_end': '#764BA2',
}


class WorkerSignals(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(str)
    status_changed = pyqtSignal(dict)
    log_message = pyqtSignal(str)


class ClawWorker(threading.Thread):
    
    def __init__(self, port: str, baudrate: int = 115200):
        super().__init__()
        self.port = port
        self.baudrate = baudrate
        self.controller = None
        self.running = True
        self.signals = WorkerSignals()
        self.daemon = True
        
    def run(self):
        try:
            self.controller = ClawController(self.port, self.baudrate)
            
            if self.controller.connect():
                self.signals.status_changed.emit({
                    "connected": True,
                    "port": self.port,
                    "angle": self.controller.current_status.angle,
                    "gripper_open": self.controller.current_status.gripper_open
                })
                self.signals.log_message.emit(f"Connected to {self.port}")
                
                while self.running:
                    pass
            else:
                self.signals.error.emit(f"Connection failed: {self.controller.current_status.error}")
                
        except Exception as e:
            self.signals.error.emit(str(e))
        finally:
            if self.controller:
                self.controller.disconnect()
            self.signals.finished.emit()
            
    def stop(self):
        self.running = False
        if self.controller:
            self.controller.disconnect()
            
    def move_angle(self, angle: int):
        if self.controller and self.controller.is_connected():
            self.controller.move_angle(angle)
            self.signals.status_changed.emit({"angle": angle})
            
    def open_gripper(self):
        if self.controller and self.controller.is_connected():
            self.controller.open_gripper()
            self.signals.status_changed.emit({"gripper_open": True})
            self.signals.log_message.emit("Gripper opened")
            
    def close_gripper(self):
        if self.controller and self.controller.is_connected():
            self.controller.close_gripper()
            self.signals.status_changed.emit({"gripper_open": False})
            self.signals.log_message.emit("Gripper closed")
            
    def full_open(self):
        if self.controller and self.controller.is_connected():
            self.controller.full_open()
            self.signals.status_changed.emit({"angle": 180, "gripper_open": True})
            self.signals.log_message.emit("Fully opened (180)")
            
    def full_close(self):
        if self.controller and self.controller.is_connected():
            self.controller.full_close()
            self.signals.status_changed.emit({"angle": 0, "gripper_open": False})
            self.signals.log_message.emit("Fully closed (0)")
            
    def grip(self):
        if self.controller and self.controller.is_connected():
            self.controller.grip()
            self.signals.status_changed.emit({"angle": 45, "gripper_open": False})
            self.signals.log_message.emit("Grip position (45)")
            
    def reset(self):
        if self.controller and self.controller.is_connected():
            self.controller.reset()
            self.signals.status_changed.emit({"angle": 90, "gripper_open": True})
            self.signals.log_message.emit("Reset (90)")


class ModernButton(QPushButton):
    
    def __init__(self, text: str, color: str = COLORS['primary'], parent=None):
        super().__init__(text, parent)
        self.color = color
        self.setFixedHeight(45)
        self.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
            }}
            QPushButton:hover {{
                background-color: {self._darken_color(color)};
            }}
            QPushButton:pressed {{
                background-color: {self._darken_color(color, 0.2)};
            }}
            QPushButton:disabled {{
                background-color: #E5E7EB;
                color: #9CA3AF;
            }}
        """)
    
    def _darken_color(self, color: str, factor: float = 0.1) -> str:
        color = color.lstrip('#')
        r, g, b = int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)
        r = max(0, int(r * (1 - factor)))
        g = max(0, int(g * (1 - factor)))
        b = max(0, int(b * (1 - factor)))
        return f"#{r:02x}{g:02x}{b:02x}"


class GradientFrame(QFrame):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: transparent;")
        
    def paintEvent(self, event):
        painter = QPainter(self)
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, QColor(COLORS['bg_gradient_start']))
        gradient.setColorAt(1, QColor(COLORS['bg_gradient_end']))
        painter.fillRect(self.rect(), gradient)


class MainWindow(QMainWindow):
    
    def __init__(self):
        super().__init__()
        self.worker = None
        self.config = get_config()
        self.log_lines = []
        self.max_log_lines = 1000
        
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("OpenClaw Toolkit - Claw Control")
        self.setGeometry(100, 100, 900, 700)
        self.setMinimumSize(800, 600)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        header = self.create_header()
        main_layout.addWidget(header)
        
        content_widget = QWidget()
        content_widget.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['light']};
            }}
        """)
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(15)
        
        connection_group = self.create_connection_group()
        content_layout.addWidget(connection_group)
        
        angle_group = self.create_angle_group()
        content_layout.addWidget(angle_group)
        
        quick_group = self.create_quick_group()
        content_layout.addWidget(quick_group)
        
        log_group = self.create_log_group()
        content_layout.addWidget(log_group)
        
        main_layout.addWidget(content_widget)
        
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet(f"""
            QStatusBar {{
                background-color: {COLORS['dark']};
                color: white;
                padding: 5px;
            }}
        """)
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Not connected")
        
        # Refresh ports after UI is ready
        self.refresh_ports()
        
    def init_ui(self):
        self.setWindowTitle("OpenClaw Toolkit - Claw Control")
        self.setGeometry(100, 100, 900, 700)
        self.setMinimumSize(800, 600)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        header = self.create_header()
        main_layout.addWidget(header)
        
        content_widget = QWidget()
        content_widget.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['light']};
            }}
        """)
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(15)
        
        connection_group = self.create_connection_group()
        content_layout.addWidget(connection_group)
        
        angle_group = self.create_angle_group()
        content_layout.addWidget(angle_group)
        
        quick_group = self.create_quick_group()
        content_layout.addWidget(quick_group)
        
        log_group = self.create_log_group()
        content_layout.addWidget(log_group)
        
        main_layout.addWidget(content_widget)
        
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet(f"""
            QStatusBar {{
                background-color: {COLORS['dark']};
                color: white;
                padding: 5px;
            }}
        """)
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Not connected")
        
    def create_header(self) -> QFrame:
        header = QFrame()
        header.setFixedHeight(70)
        header.setStyleSheet("background-color: transparent;")
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(25, 0, 25, 0)
        
        title_label = QLabel("OpenClaw Toolkit")
        title_label.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title_label.setStyleSheet("color: white; background: transparent;")
        
        subtitle = QLabel("Open Source Claw Controller")
        subtitle.setFont(QFont("Segoe UI", 10))
        subtitle.setStyleSheet("color: rgba(255,255,255,0.8); background: transparent;")
        
        title_layout = QVBoxLayout()
        title_layout.addWidget(title_label)
        title_layout.addWidget(subtitle)
        title_layout.setSpacing(0)
        
        layout.addLayout(title_layout)
        layout.addStretch()
        
        version = QLabel("v1.0.0")
        version.setFont(QFont("Segoe UI", 9))
        version.setStyleSheet("color: rgba(255,255,255,0.6); background: transparent; padding: 5px 10px; border: 1px solid rgba(255,255,255,0.3); border-radius: 12px;")
        layout.addWidget(version)
        
        header.paintEvent = lambda e: self._paint_header(e, header)
        
        return header
    
    def _paint_header(self, event, widget):
        painter = QPainter(widget)
        gradient = QLinearGradient(0, 0, widget.width(), 0)
        gradient.setColorAt(0, QColor(COLORS['bg_gradient_start']))
        gradient.setColorAt(0.5, QColor(COLORS['bg_gradient_end']))
        gradient.setColorAt(1, QColor(COLORS['primary']))
        painter.fillRect(widget.rect(), gradient)
        
    def create_connection_group(self) -> QGroupBox:
        group = QGroupBox("Connection")
        group.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
        group.setStyleSheet(f"""
            QGroupBox {{
                background-color: white;
                border: 1px solid #E5E7EB;
                border-radius: 12px;
                padding: 15px;
                margin-top: 10px;
            }}
            QGroupBox::title {{
                color: {COLORS['dark']};
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 5px 10px;
            }}
        """)
        
        layout = QHBoxLayout()
        layout.setSpacing(15)
        
        port_label = QLabel("Port:")
        port_label.setFont(QFont("Segoe UI", 10))
        self.port_combo = QComboBox()
        self.port_combo.setMinimumWidth(150)
        self.port_combo.setStyleSheet(f"""
            QComboBox {{
                border: 1px solid #D1D5DB;
                border-radius: 6px;
                padding: 8px 12px;
                background-color: white;
                min-height: 25px;
            }}
            QComboBox:hover {{
                border-color: {COLORS['primary']};
            }}
        """)
        
        refresh_btn = ModernButton("Refresh", COLORS['gray'])
        refresh_btn.setFixedWidth(80)
        refresh_btn.clicked.connect(self.refresh_ports)
        refresh_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #6B7280;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
            }}
            QPushButton:hover {{
                background-color: #4B5563;
            }}
        """)
        
        baudrate_label = QLabel("Baudrate:")
        baudrate_label.setFont(QFont("Segoe UI", 10))
        self.baudrate_combo = QComboBox()
        self.baudrate_combo.addItems(["9600", "19200", "38400", "57600", "115200", "230400", "460800", "921600"])
        self.baudrate_combo.setCurrentText("115200")
        self.baudrate_combo.setMinimumWidth(100)
        self.baudrate_combo.setStyleSheet(self.port_combo.styleSheet())
        
        self.connect_btn = ModernButton("Connect", COLORS['primary'])
        self.connect_btn.setFixedWidth(100)
        self.connect_btn.clicked.connect(self.toggle_connection)
        
        layout.addWidget(port_label)
        layout.addWidget(self.port_combo)
        layout.addWidget(refresh_btn)
        layout.addWidget(baudrate_label)
        layout.addWidget(self.baudrate_combo)
        layout.addWidget(self.connect_btn)
        layout.addStretch()
        
        group.setLayout(layout)
        return group
        
    def create_angle_group(self) -> QGroupBox:
        group = QGroupBox("Angle Control")
        group.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
        group.setStyleSheet(self.create_connection_group().styleSheet())
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        angle_display = QHBoxLayout()
        angle_display.addWidget(QLabel("Current Angle:"))
        
        self.angle_label = QLabel("90")
        self.angle_label.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        self.angle_label.setStyleSheet(f"color: {COLORS['primary']}; min-width: 100px;")
        angle_display.addWidget(self.angle_label)
        angle_display.addStretch()
        
        self.angle_slider = QSlider(Qt.Orientation.Horizontal)
        self.angle_slider.setMinimum(0)
        self.angle_slider.setMaximum(180)
        self.angle_slider.setValue(90)
        self.angle_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.angle_slider.setTickInterval(30)
        self.angle_slider.valueChanged.connect(self.on_angle_changed)
        self.angle_slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                border: 1px solid #D1D5DB;
                height: 8px;
                background: #E5E7EB;
                border-radius: 4px;
            }}
            QSlider::handle:horizontal {{
                background: {COLORS['primary']};
                border: 2px solid white;
                width: 24px;
                margin: -8px 0;
                border-radius: 12px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.2);
            }}
            QSlider::sub-page:horizontal {{
                background: {COLORS['primary']};
                border-radius: 4px;
            }}
        """)
        
        preset_layout = QHBoxLayout()
        preset_layout.setSpacing(10)
        
        for angle, label, color in [
            (0, "0", COLORS['danger']),
            (45, "45", COLORS['warning']),
            (90, "90", COLORS['primary']),
            (135, "135", COLORS['warning']),
            (180, "180", COLORS['secondary'])
        ]:
            btn = ModernButton(label, color)
            btn.setFixedHeight(35)
            btn.clicked.connect(lambda checked, a=angle: self.set_angle(a))
            preset_layout.addWidget(btn)
            
        preset_layout.addStretch()
        
        layout.addLayout(angle_display)
        layout.addWidget(self.angle_slider)
        layout.addLayout(preset_layout)
        
        group.setLayout(layout)
        return group
        
    def create_quick_group(self) -> QGroupBox:
        group = QGroupBox("Quick Actions")
        group.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
        group.setStyleSheet(self.create_connection_group().styleSheet())
        
        layout = QHBoxLayout()
        layout.setSpacing(15)
        
        self.full_open_btn = ModernButton("Full Open (180)", COLORS['secondary'])
        self.full_open_btn.clicked.connect(self.on_full_open)
        
        self.grip_btn = ModernButton("Grip (45)", COLORS['warning'])
        self.grip_btn.clicked.connect(self.on_grip)
        
        self.full_close_btn = ModernButton("Full Close (0)", COLORS['danger'])
        self.full_close_btn.clicked.connect(self.on_full_close)
        
        self.reset_btn = ModernButton("Reset (90)", COLORS['gray'])
        self.reset_btn.clicked.connect(self.on_reset)
        
        layout.addWidget(self.full_open_btn)
        layout.addWidget(self.grip_btn)
        layout.addWidget(self.full_close_btn)
        layout.addWidget(self.reset_btn)
        layout.addStretch()
        
        group.setLayout(layout)
        return group
        
    def create_log_group(self) -> QGroupBox:
        group = QGroupBox("Log")
        group.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
        group.setStyleSheet(self.create_connection_group().styleSheet())
        
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150)
        self.log_text.setFont(QFont("Consolas", 9))
        self.log_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: {COLORS['dark']};
                color: #10B981;
                border: 1px solid #374151;
                border-radius: 8px;
                padding: 10px;
            }}
        """)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        clear_btn = ModernButton("Clear", COLORS['gray'])
        clear_btn.setFixedWidth(80)
        clear_btn.setFixedHeight(30)
        clear_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #6B7280;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 5px 10px;
            }}
            QPushButton:hover {{
                background-color: #4B5563;
            }}
        """)
        clear_btn.clicked.connect(self.clear_log)
        
        btn_layout.addWidget(clear_btn)
        
        layout.addWidget(self.log_text)
        layout.addLayout(btn_layout)
        
        group.setLayout(layout)
        return group
        
    def refresh_ports(self):
        self.port_combo.clear()
        
        ports = scan_ports()
        
        if ports:
            for port in ports:
                self.port_combo.addItem(port)
        else:
            self.port_combo.addItem("No port found")
            self.log_message("No available port")
            
    def toggle_connection(self):
        if self.worker and self.worker.is_alive():
            self.disconnect()
        else:
            self.connect()
            
    def connect(self):
        port = self.port_combo.currentText()
        
        if not port or port == "No port found":
            QMessageBox.warning(self, "Warning", "Please select a valid port")
            return
            
        baudrate = int(self.baudrate_combo.currentText())
        
        self.log_message(f"Connecting to {port} @ {baudrate}bps...")
        self.connect_btn.setEnabled(False)
        self.connect_btn.setText("Connecting...")
        
        self.worker = ClawWorker(port, baudrate)
        self.worker.signals.status_changed.connect(self.on_status_changed)
        self.worker.signals.log_message.connect(self.log_message)
        self.worker.signals.error.connect(self.on_connection_error)
        self.worker.start()
        
    def disconnect(self):
        if self.worker:
            self.worker.stop()
            self.worker = None
            
        self.connect_btn.setText("Connect")
        self.connect_btn.setEnabled(True)
        self.connect_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['primary']};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['primary_dark']};
            }}
        """)
        self.status_bar.showMessage("Not connected")
        self.log_message("Disconnected")
        
    @pyqtSlot(dict)
    def on_status_changed(self, status: dict):
        if status.get("connected"):
            self.connect_btn.setText("Disconnect")
            self.connect_btn.setEnabled(True)
            self.connect_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLORS['danger']};
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 10px 20px;
                }}
                QPushButton:hover {{
                    background-color: #DC2626;
                }}
            """)
            self.status_bar.showMessage(f"Connected: {status.get('port')}")
            
        if "angle" in status:
            self.angle_label.setText(f"{status['angle']}")
            if not self.angle_slider.isSliderDown():
                self.angle_slider.setValue(status['angle'])
                
    @pyqtSlot(str)
    def log_message(self, msg: str):
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_lines.append(f"[{timestamp}] {msg}")
        
        if len(self.log_lines) > self.max_log_lines:
            self.log_lines = self.log_lines[-self.max_log_lines:]
            
        self.log_text.setPlainText("\n".join(self.log_lines))
        self.log_text.verticalScrollBar().setValue(self.log_text.verticalScrollBar().maximum())
        
    @pyqtSlot(str)
    def on_connection_error(self, error: str):
        self.connect_btn.setText("Connect")
        self.connect_btn.setEnabled(True)
        self.connect_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['primary']};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
            }}
        """)
        self.status_bar.showMessage("Connection failed")
        QMessageBox.critical(self, "Error", error)
        
    def on_angle_changed(self, value: int):
        self.angle_label.setText(f"{value}")
        
        if self.worker and self.worker.is_alive():
            self.worker.move_angle(value)
            
    def set_angle(self, angle: int):
        self.angle_slider.setValue(angle)
        
    def on_full_open(self):
        if self.worker and self.worker.is_alive():
            self.worker.full_open()
            
    def on_full_close(self):
        if self.worker and self.worker.is_alive():
            self.worker.full_close()
            
    def on_grip(self):
        if self.worker and self.worker.is_alive():
            self.worker.grip()
            
    def on_reset(self):
        if self.worker and self.worker.is_alive():
            self.worker.reset()
            
    def clear_log(self):
        self.log_lines.clear()
        self.log_text.clear()
        
    def closeEvent(self, event):
        if self.worker:
            self.worker.stop()
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    app.setStyleSheet(f"""
        QMainWindow {{
            background-color: {COLORS['light']};
        }}
    """)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
