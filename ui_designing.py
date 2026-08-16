import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QFrame, QPushButton, QDialog,
                             QSlider, QGraphicsOpacityEffect, QStackedWidget)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint, QSize, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QPen, QFont, QPainterPath, QLinearGradient, QRadialGradient
from datetime import datetime
import math
import requests
import json
import random

# Dark Theme Color Palette
COLORS = {
    'bg': '#000000',
    'primary': '#1a1a1a',
    'secondary': '#2d2d2d',
    'accent': '#FFFFFF',
    'light': '#EFDCCB',
    'active': '#00ff41',
    'cyan': '#00F0FF',
    'emergency': '#FF0000',
    'text_primary': '#FFFFFF',
    'text_secondary': '#B0B0B0',
    'card_bg': '#1a1a1a'
}

class StatusIndicator(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(40, 40)
        self.pulse_radius = 0
        self.pulse_opacity = 1.0
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_pulse)
        self.timer.start(50)
        
    def update_pulse(self):
        self.pulse_radius += 1
        self.pulse_opacity -= 0.02
        
        if self.pulse_radius > 20:
            self.pulse_radius = 0
            self.pulse_opacity = 1.0
        
        self.update()
   
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        if self.pulse_opacity > 0:
            color = QColor(COLORS['active'])
            color.setAlphaF(self.pulse_opacity * 0.5)
            pen = QPen(color, 2)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            
            radius = 10 + self.pulse_radius
            center = self.rect().center()
            painter.drawEllipse(center, radius, radius)
        
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(COLORS['active']))
        painter.drawEllipse(self.rect().center(), 10, 10)

class TemperatureWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        layout.setAlignment(Qt.AlignCenter)
        
        self.weather_label = QLabel("Loading")
        self.weather_label.setFont(QFont('Arial', 14))
        self.weather_label.setAlignment(Qt.AlignCenter)
        self.weather_label.setStyleSheet(f"color: {COLORS['text_secondary']}; background: transparent;")
        layout.addWidget(self.weather_label)
        
        self.value_label = QLabel("--°C")
        self.value_label.setFont(QFont('Arial', 22, QFont.Bold))
        self.value_label.setAlignment(Qt.AlignCenter)
        self.value_label.setStyleSheet(f"color: {COLORS['accent']}; background: transparent;")
        layout.addWidget(self.value_label)
        
        self.setLayout(layout)
   
    def update_weather(self, temp, weather_desc):
        self.value_label.setText(f"{temp}°C")
        self.weather_label.setText(weather_desc)

class AnimatedSpeaker(QWidget):
    """Animated speaking visualization with waveform bars"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(300, 300)
        self.is_speaking = False
        self.bars = []
        self.num_bars = 5
        
        for i in range(self.num_bars):
            self.bars.append({
                'height': random.uniform(0.2, 0.8),
                'target': random.uniform(0.2, 0.8),
                'speed': random.uniform(0.05, 0.15)
            })
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.animate)
        self.timer.start(50)
        
    def start_speaking(self):
        self.is_speaking = True
        
    def stop_speaking(self):
        self.is_speaking = False
        
    def animate(self):
        if self.is_speaking:
            for bar in self.bars:
                if abs(bar['height'] - bar['target']) < 0.05:
                    bar['target'] = random.uniform(0.3, 1.0)
                else:
                    if bar['height'] < bar['target']:
                        bar['height'] += bar['speed']
                    else:
                        bar['height'] -= bar['speed']
        else:
            for bar in self.bars:
                bar['target'] = 0.2
                if bar['height'] > 0.2:
                    bar['height'] -= 0.02
        
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        painter.setPen(Qt.NoPen)
        
        gradient = QRadialGradient(self.rect().center(), 130)
        gradient.setColorAt(0, QColor(COLORS['cyan']).darker(200))
        gradient.setColorAt(0.7, QColor(COLORS['bg']))
        gradient.setColorAt(1, QColor(COLORS['bg']))
        painter.setBrush(gradient)
        painter.drawEllipse(self.rect().center(), 130, 130)
        
        painter.setBrush(QColor(COLORS['primary']))
        painter.drawEllipse(self.rect().center(), 120, 120)
        
        center_x = self.rect().center().x()
        center_y = self.rect().center().y()
        bar_width = 8
        spacing = 16
        max_height = 80
        
        for i, bar in enumerate(self.bars):
            x = center_x + (i - self.num_bars // 2) * spacing
            height = bar['height'] * max_height
            
            bar_gradient = QLinearGradient(x, center_y - height/2, x, center_y + height/2)
            bar_gradient.setColorAt(0, QColor(COLORS['cyan']))
            bar_gradient.setColorAt(1, QColor('#FFFFFF'))
            
            painter.setBrush(bar_gradient)
            painter.setPen(Qt.NoPen)
            
            rect_x = x - bar_width // 2
            rect_y = center_y - height // 2
            painter.drawRoundedRect(int(rect_x), int(rect_y), bar_width, int(height), 4, 4)
        
        painter.setPen(QPen(QColor(COLORS['text_primary']), 2))
        painter.setBrush(Qt.NoBrush)
        
        mic_center_y = center_y + 60
        painter.drawRoundedRect(center_x - 15, mic_center_y - 20, 30, 35, 15, 15)
        
        painter.drawLine(center_x, mic_center_y + 15, center_x, mic_center_y + 30)
        painter.drawLine(center_x - 12, mic_center_y + 30, center_x + 12, mic_center_y + 30)

class VoiceListeningIndicator(QWidget):
    """Small animated indicator for listening state"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(30, 30)
        self.angle = 0
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.rotate)
        self.timer.start(50)
        
    def rotate(self):
        self.angle = (self.angle + 10) % 360
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        painter.translate(self.rect().center())
        painter.rotate(self.angle)
        
        pen = QPen(QColor(COLORS['cyan']), 3)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        
        painter.drawArc(-10, -10, 20, 20, 0, 270 * 16)

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setFixedSize(500, 450)  # Increased height for close button
        self.selected_control = 0  # 0=brightness, 1=volume, 2=close
        self.is_editing = False
        self.control_highlighted = False  # Track if a control is highlighted for selection
        
        dialog_stylesheet = '''QDialog {
    background-color: ''' + COLORS['bg'] + ''';
    color: ''' + COLORS['text_primary'] + ''';
}
QLabel {
    color: ''' + COLORS['text_primary'] + ''';
    border: none;
    background: transparent;
}
QSlider::groove:horizontal {
    height: 10px;
    background: ''' + COLORS['secondary'] + ''';
    margin: 0px;
    border-radius: 5px;
}
QSlider::sub-page:horizontal {
    height: 10px;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 ''' + COLORS['cyan'] + ''', stop:1 #FFFFFF);
    border-radius: 5px;
}
QSlider::add-page:horizontal {
    height: 10px;
    background: ''' + COLORS['secondary'] + ''';
    border-radius: 5px;
}
QSlider::handle:horizontal {
    background: #FFFFFF;
    border: 3px solid ''' + COLORS['bg'] + ''';
    width: 24px;
    height: 24px;
    margin: -7px 0;
    border-radius: 12px;
}
QSlider::handle:horizontal:hover {
    background: ''' + COLORS['cyan'] + ''';
}'''
        self.setStyleSheet(dialog_stylesheet)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(30)
        
        # Title
        title = QLabel("⚙️ Device Settings")
        title.setFont(QFont('Arial', 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)
        
        main_layout.addSpacing(10)
        
        # Brightness control
        brightness_container = QVBoxLayout()
        brightness_container.setSpacing(12)
        brightness_container.setContentsMargins(0, 0, 0, 0)
        
        # Brightness header
        brightness_header = QHBoxLayout()
        brightness_header.setContentsMargins(0, 0, 0, 0)
        
        brightness_label = QLabel("💡 Brightness")
        brightness_label.setFont(QFont('Arial', 14, QFont.Bold))
        brightness_label.setStyleSheet("background: transparent; color: #FFFFFF; border: none; padding: 0px; margin: 0px;")
        brightness_label.setTextFormat(Qt.PlainText)
        brightness_label.adjustSize()
        brightness_header.addWidget(brightness_label)
        brightness_header.addStretch()
        
        self.brightness_value = QLabel(f"{self.parent().brightness}%")
        self.brightness_value.setFont(QFont('Arial', 14, QFont.Bold))
        self.brightness_value.setStyleSheet(f"color: {COLORS['text_secondary']}; background: transparent; border: none; padding: 0px; margin: 0px;")
        self.brightness_value.setTextFormat(Qt.PlainText)
        self.brightness_value.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.brightness_value.setMinimumWidth(50)
        brightness_header.addWidget(self.brightness_value)
        
        brightness_container.addLayout(brightness_header)
        
        # Brightness slider
        self.brightness_slider = QSlider(Qt.Horizontal)
        self.brightness_slider.setRange(0, 100)
        self.brightness_slider.setValue(self.parent().brightness)
        self.brightness_slider.setMinimumHeight(30)
        self.brightness_slider.setEnabled(False)
        self.brightness_slider.setStyleSheet("background: transparent;")
        brightness_container.addWidget(self.brightness_slider)
        
        # Wrap in frame for visual feedback - ALWAYS show border
        self.brightness_frame = QFrame()
        self.brightness_frame.setLayout(brightness_container)
        self.brightness_frame.setStyleSheet(f"""QFrame {{ 
            background: transparent; 
            border: 2px solid {COLORS['secondary']}; 
            padding: 15px; 
            border-radius: 10px; 
        }}""")
        main_layout.addWidget(self.brightness_frame)
        main_layout.addSpacing(15)
        
        # Volume control
        volume_container = QVBoxLayout()
        volume_container.setSpacing(12)
        volume_container.setContentsMargins(0, 0, 0, 0)
        
        # Volume header
        volume_header = QHBoxLayout()
        volume_header.setContentsMargins(0, 0, 0, 0)
        
        volume_label = QLabel("🔊 Volume")
        volume_label.setFont(QFont('Arial', 14, QFont.Bold))
        volume_label.setStyleSheet("background: transparent; color: #FFFFFF; border: none; padding: 0px; margin: 0px;")
        volume_label.setTextFormat(Qt.PlainText)
        volume_label.adjustSize()
        volume_header.addWidget(volume_label)
        volume_header.addStretch()
        
        self.volume_value = QLabel(f"{self.parent().volume}%")
        self.volume_value.setFont(QFont('Arial', 14, QFont.Bold))
        self.volume_value.setStyleSheet(f"color: {COLORS['text_secondary']}; background: transparent; border: none; padding: 0px; margin: 0px;")
        self.volume_value.setTextFormat(Qt.PlainText)
        self.volume_value.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.volume_value.setMinimumWidth(50)
        volume_header.addWidget(self.volume_value)
        
        volume_container.addLayout(volume_header)
        
        # Volume slider
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(self.parent().volume)
        self.volume_slider.setMinimumHeight(30)
        self.volume_slider.setEnabled(False)
        self.volume_slider.setStyleSheet("background: transparent;")
        volume_container.addWidget(self.volume_slider)
        
        # Wrap in frame for visual feedback - ALWAYS show border
        self.volume_frame = QFrame()
        self.volume_frame.setLayout(volume_container)
        self.volume_frame.setStyleSheet(f"""QFrame {{ 
            background: transparent; 
            border: 2px solid {COLORS['secondary']}; 
            padding: 15px; 
            border-radius: 10px; 
        }}""")
        main_layout.addWidget(self.volume_frame)
        
        main_layout.addSpacing(20)
        
        # Close button
        close_container = QHBoxLayout()
        close_container.setContentsMargins(0, 0, 0, 0)
        
        close_button_label = QLabel("✖️  Close Settings")
        close_button_label.setFont(QFont('Arial', 14, QFont.Bold))
        close_button_label.setStyleSheet("background: transparent; color: #FFFFFF; border: none; padding: 0px; margin: 0px;")
        close_button_label.setAlignment(Qt.AlignCenter)
        close_button_label.setTextFormat(Qt.PlainText)
        close_button_label.adjustSize()
        close_button_label.setMinimumWidth(200)
        close_container.addWidget(close_button_label)
        
        self.close_frame = QFrame()
        self.close_frame.setLayout(close_container)
        self.close_frame.setStyleSheet(f"""QFrame {{ 
            background: transparent; 
            border: 2px solid {COLORS['secondary']}; 
            padding: 15px; 
            border-radius: 10px; 
        }}""")
        main_layout.addWidget(self.close_frame)
        
        main_layout.addStretch()
        
        # Info text
        self.info_label = QLabel("🔄 Rotate to select control")
        self.info_label.setFont(QFont('Arial', 12, QFont.Bold))
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setStyleSheet(f"color: {COLORS['text_secondary']}; background: transparent;")
        main_layout.addWidget(self.info_label)
        
        self.setLayout(main_layout)
        
        self.brightness_slider.valueChanged.connect(lambda v: self.brightness_value.setText(f"{v}%"))
        self.volume_slider.valueChanged.connect(lambda v: self.volume_value.setText(f"{v}%"))
        
        # Start with no control highlighted
        self.update_ui_state()
    
    def keyPressEvent(self, event):
        """Handle encoder input - same mechanism as main screen button selection"""
        
        if not self.is_editing:
            # Step 1 & 2: Highlighting mode - NO slider changes!
            if event.key() == Qt.Key_Up or event.key() == Qt.Key_Left or event.key() == Qt.Key_Down or event.key() == Qt.Key_Right:
                # First rotation: highlight a control, subsequent rotations: switch between controls
                if not self.control_highlighted:
                    # First rotation - highlight the first control (brightness)
                    self.control_highlighted = True
                    self.selected_control = 0
                    print("► Brightness HIGHLIGHTED (press Enter to start editing)")
                else:
                    # Already highlighted - cycle between brightness, volume, and close
                    if event.key() == Qt.Key_Down or event.key() == Qt.Key_Right:
                        # Rotate down/right - next option
                        self.selected_control = (self.selected_control + 1) % 3
                        if self.selected_control == 0:
                            print("► Brightness HIGHLIGHTED (press Enter to start editing)")
                        elif self.selected_control == 1:
                            print("► Volume HIGHLIGHTED (press Enter to start editing)")
                        else:
                            print("► Close HIGHLIGHTED (press Enter to close settings)")
                    else:  # Up or Left
                        # Rotate up/left - previous option
                        self.selected_control = (self.selected_control - 1) % 3
                        if self.selected_control == 0:
                            print("► Brightness HIGHLIGHTED (press Enter to start editing)")
                        elif self.selected_control == 1:
                            print("► Volume HIGHLIGHTED (press Enter to start editing)")
                        else:
                            print("► Close HIGHLIGHTED (press Enter to close settings)")
                
                self.update_ui_state()
                event.accept()
                
            elif event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
                if self.control_highlighted:
                    # Check if Close button is selected
                    if self.selected_control == 2:
                        print("✓ Settings closed\n")
                        self.accept()
                        event.accept()
                        return
                    
                    # Control is highlighted - enter editing mode
                    self.is_editing = True
                    self.update_ui_state()
                    if self.selected_control == 0:
                        print("✎ NOW EDITING Brightness (rotate to adjust, press Enter to save)")
                    else:
                        print("✎ NOW EDITING Volume (rotate to adjust, press Enter to save)")
                else:
                    # Nothing highlighted yet - first press highlights brightness
                    self.control_highlighted = True
                    self.selected_control = 0
                    self.update_ui_state()
                    print("► Brightness HIGHLIGHTED (press Enter again to start editing)")
                event.accept()
        
        else:
            # Step 3: Editing mode - NOW sliders can change!
            if event.key() == Qt.Key_Down or event.key() == Qt.Key_Left:
                # Rotate CCW - DECREASE value
                if self.selected_control == 0:
                    new_val = max(0, self.brightness_slider.value() - 5)
                    self.brightness_slider.blockSignals(True)
                    self.brightness_slider.setValue(new_val)
                    self.brightness_slider.blockSignals(False)
                    self.brightness_value.setText(f"{new_val}%")  # Update display
                    self.parent().change_brightness(new_val)  # Apply change
                    print(f"Brightness: {new_val}% ◄")
                else:
                    new_val = max(0, self.volume_slider.value() - 5)
                    self.volume_slider.blockSignals(True)
                    self.volume_slider.setValue(new_val)
                    self.volume_slider.blockSignals(False)
                    self.volume_value.setText(f"{new_val}%")  # Update display
                    self.parent().change_volume(new_val)  # Apply change
                    print(f"Volume: {new_val}% ◄")
                event.accept()
                
            elif event.key() == Qt.Key_Up or event.key() == Qt.Key_Right:
                # Rotate CW - INCREASE value
                if self.selected_control == 0:
                    new_val = min(100, self.brightness_slider.value() + 5)
                    self.brightness_slider.blockSignals(True)
                    self.brightness_slider.setValue(new_val)
                    self.brightness_slider.blockSignals(False)
                    self.brightness_value.setText(f"{new_val}%")  # Update display
                    self.parent().change_brightness(new_val)  # Apply change
                    print(f"Brightness: {new_val}% ►")
                else:
                    new_val = min(100, self.volume_slider.value() + 5)
                    self.volume_slider.blockSignals(True)
                    self.volume_slider.setValue(new_val)
                    self.volume_slider.blockSignals(False)
                    self.volume_value.setText(f"{new_val}%")  # Update display
                    self.parent().change_volume(new_val)  # Apply change
                    print(f"Volume: {new_val}% ►")
                event.accept()
                
            elif event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
                # Step 4: Press - save and go back to selection mode (don't close!)
                self.is_editing = False
                if self.selected_control == 0:
                    print(f"✓ Brightness saved: {self.brightness_slider.value()}%")
                    print("← Back to selection mode (rotate to switch, Enter to edit again)")
                else:
                    print(f"✓ Volume saved: {self.volume_slider.value()}%")
                    print("← Back to selection mode (rotate to switch, Enter to edit again)")
                self.update_ui_state()
                event.accept()
    
    def update_ui_state(self):
        """Update visual indicators with colored boxes for selection/editing"""
        if not self.control_highlighted:
            # No control highlighted yet - show default gray borders
            self.brightness_frame.setStyleSheet(f"""QFrame {{ 
                background: transparent; 
                border: 2px solid {COLORS['secondary']}; 
                padding: 15px; 
                border-radius: 10px; 
            }}""")
            self.brightness_value.setStyleSheet(f"color: {COLORS['text_secondary']}; background: transparent; border: none; padding: 0px; margin: 0px;")
            
            self.volume_frame.setStyleSheet(f"""QFrame {{ 
                background: transparent; 
                border: 2px solid {COLORS['secondary']}; 
                padding: 15px; 
                border-radius: 10px; 
            }}""")
            self.volume_value.setStyleSheet(f"color: {COLORS['text_secondary']}; background: transparent; border: none; padding: 0px; margin: 0px;")
            
            self.close_frame.setStyleSheet(f"""QFrame {{ 
                background: transparent; 
                border: 2px solid {COLORS['secondary']}; 
                padding: 15px; 
                border-radius: 10px; 
            }}""")
            
            self.info_label.setText("🔄 Rotate to select control")
            self.info_label.setStyleSheet(f"color: {COLORS['text_secondary']}; background: transparent;")
            
        elif self.is_editing:
            # Editing mode - GREEN box with thick border for active
            if self.selected_control == 0:
                # Brightness editing - GREEN with thick border
                self.brightness_frame.setStyleSheet(f"""QFrame {{ 
                    background: rgba(0, 255, 65, 0.1); 
                    border: 4px solid {COLORS['active']}; 
                    padding: 15px; 
                    border-radius: 10px; 
                }}""")
                self.brightness_value.setStyleSheet(f"color: {COLORS['active']}; background: transparent; font-weight: bold; border: none; padding: 0px; margin: 0px;")
                
                # Volume - normal gray border
                self.volume_frame.setStyleSheet(f"""QFrame {{ 
                    background: transparent; 
                    border: 2px solid {COLORS['secondary']}; 
                    padding: 15px; 
                    border-radius: 10px; 
                }}""")
                self.volume_value.setStyleSheet(f"color: {COLORS['text_secondary']}; background: transparent; border: none; padding: 0px; margin: 0px;")
            else:
                # Volume editing - GREEN with thick border
                self.volume_frame.setStyleSheet(f"""QFrame {{ 
                    background: rgba(0, 255, 65, 0.1); 
                    border: 4px solid {COLORS['active']}; 
                    padding: 15px; 
                    border-radius: 10px; 
                }}""")
                self.volume_value.setStyleSheet(f"color: {COLORS['active']}; background: transparent; font-weight: bold; border: none; padding: 0px; margin: 0px;")
                
                # Brightness - normal gray border
                self.brightness_frame.setStyleSheet(f"""QFrame {{ 
                    background: transparent; 
                    border: 2px solid {COLORS['secondary']}; 
                    padding: 15px; 
                    border-radius: 10px; 
                }}""")
                self.brightness_value.setStyleSheet(f"color: {COLORS['text_secondary']}; background: transparent; border: none; padding: 0px; margin: 0px;")
            
            # Close button always gray during editing
            self.close_frame.setStyleSheet(f"""QFrame {{ 
                background: transparent; 
                border: 2px solid {COLORS['secondary']}; 
                padding: 15px; 
                border-radius: 10px; 
            }}""")
            
            self.info_label.setText("◄ Rotate to adjust • Press Enter to save ►")
            self.info_label.setStyleSheet(f"color: {COLORS['active']}; background: transparent;")
            
        else:
            # Highlighted but not editing - CYAN border with slight tint
            if self.selected_control == 0:
                # Brightness highlighted - CYAN with thicker border
                self.brightness_frame.setStyleSheet(f"""QFrame {{ 
                    background: rgba(0, 240, 255, 0.05); 
                    border: 3px solid {COLORS['cyan']}; 
                    padding: 15px; 
                    border-radius: 10px; 
                }}""")
                self.brightness_value.setStyleSheet(f"color: {COLORS['cyan']}; background: transparent; font-weight: bold; border: none; padding: 0px; margin: 0px;")
                
                # Volume - normal gray border
                self.volume_frame.setStyleSheet(f"""QFrame {{ 
                    background: transparent; 
                    border: 2px solid {COLORS['secondary']}; 
                    padding: 15px; 
                    border-radius: 10px; 
                }}""")
                self.volume_value.setStyleSheet(f"color: {COLORS['text_secondary']}; background: transparent; border: none; padding: 0px; margin: 0px;")
                
                # Close - normal gray border
                self.close_frame.setStyleSheet(f"""QFrame {{ 
                    background: transparent; 
                    border: 2px solid {COLORS['secondary']}; 
                    padding: 15px; 
                    border-radius: 10px; 
                }}""")
                
            elif self.selected_control == 1:
                # Volume highlighted - CYAN with thicker border
                self.volume_frame.setStyleSheet(f"""QFrame {{ 
                    background: rgba(0, 240, 255, 0.05); 
                    border: 3px solid {COLORS['cyan']}; 
                    padding: 15px; 
                    border-radius: 10px; 
                }}""")
                self.volume_value.setStyleSheet(f"color: {COLORS['cyan']}; background: transparent; font-weight: bold; border: none; padding: 0px; margin: 0px;")
                
                # Brightness - normal gray border
                self.brightness_frame.setStyleSheet(f"""QFrame {{ 
                    background: transparent; 
                    border: 2px solid {COLORS['secondary']}; 
                    padding: 15px; 
                    border-radius: 10px; 
                }}""")
                self.brightness_value.setStyleSheet(f"color: {COLORS['text_secondary']}; background: transparent; border: none; padding: 0px; margin: 0px;")
                
                # Close - normal gray border
                self.close_frame.setStyleSheet(f"""QFrame {{ 
                    background: transparent; 
                    border: 2px solid {COLORS['secondary']}; 
                    padding: 15px; 
                    border-radius: 10px; 
                }}""")
                
            else:  # selected_control == 2 (Close button)
                # Close highlighted - RED with thicker border
                self.close_frame.setStyleSheet(f"""QFrame {{ 
                    background: rgba(255, 0, 0, 0.05); 
                    border: 3px solid #FF0044; 
                    padding: 15px; 
                    border-radius: 10px; 
                }}""")
                
                # Brightness - normal gray border
                self.brightness_frame.setStyleSheet(f"""QFrame {{ 
                    background: transparent; 
                    border: 2px solid {COLORS['secondary']}; 
                    padding: 15px; 
                    border-radius: 10px; 
                }}""")
                self.brightness_value.setStyleSheet(f"color: {COLORS['text_secondary']}; background: transparent; border: none; padding: 0px; margin: 0px;")
                
                # Volume - normal gray border
                self.volume_frame.setStyleSheet(f"""QFrame {{ 
                    background: transparent; 
                    border: 2px solid {COLORS['secondary']}; 
                    padding: 15px; 
                    border-radius: 10px; 
                }}""")
                self.volume_value.setStyleSheet(f"color: {COLORS['text_secondary']}; background: transparent; border: none; padding: 0px; margin: 0px;")
            
            self.info_label.setText("⏎ Press Enter to activate")
            self.info_label.setStyleSheet(f"color: {COLORS['cyan']}; background: transparent;")
    
    def on_brightness_changed(self, value):
        """Slider visual update only - actual brightness change happens in keyPressEvent"""
        pass
    
    def on_volume_changed(self, value):
        """Slider visual update only - actual volume change happens in keyPressEvent"""
        pass

class MainScreen(QWidget):
    """Main clock/weather display screen"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_button = 0  # 0=settings, 1=emergency
        self.setup_ui()
        
    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 20, 10, 20)
        main_layout.setSpacing(15)
        
        # Top row: Status and buttons
        top_row = QHBoxLayout()
        top_row.setSpacing(12)
        
        status_container = QHBoxLayout()
        status_container.setSpacing(8)
        
        self.status_indicator = StatusIndicator()
        status_container.addWidget(self.status_indicator)
        
        status_label = QLabel("ACTIVE")
        status_label.setFont(QFont('Arial', 11, QFont.Bold))
        status_label.setStyleSheet(f"color: {COLORS['active']}; background: transparent;")
        status_container.addWidget(status_label)
        status_container.addStretch()
        
        top_row.addLayout(status_container)
        top_row.addStretch()
        
        # Settings button
        self.settings_button = QPushButton("⚙️ Settings")
        self.settings_button.setFont(QFont('Arial', 10))
        self.settings_button.setFocusPolicy(Qt.NoFocus)
        top_row.addWidget(self.settings_button)
        
        # Emergency button
        self.emergency_button = QPushButton("🚨 Emergency")
        self.emergency_button.setFont(QFont('Arial', 10))
        self.emergency_button.setFocusPolicy(Qt.NoFocus)
        top_row.addWidget(self.emergency_button)
        
        main_layout.addLayout(top_row)
        main_layout.addSpacing(40)
        
        # Weather at top center
        weather_container = QVBoxLayout()
        weather_container.setSpacing(5)
        weather_container.setAlignment(Qt.AlignCenter)
        
        self.temp_widget = TemperatureWidget()
        weather_container.addWidget(self.temp_widget, alignment=Qt.AlignCenter)
        
        main_layout.addLayout(weather_container)
        main_layout.addSpacing(20)
        
        # Time display
        self.time_label = QLabel("09:47")
        self.time_label.setFont(QFont('Arial', 90, QFont.Bold))
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setStyleSheet(f"color: {COLORS['accent']}; background: transparent;")
        main_layout.addWidget(self.time_label)
        
        main_layout.addSpacing(10)
        
        # Date
        self.date_label = QLabel("3rd of November 2025")
        self.date_label.setFont(QFont('Arial', 18))
        self.date_label.setAlignment(Qt.AlignCenter)
        self.date_label.setStyleSheet(f"color: {COLORS['text_secondary']}; background: transparent;")
        main_layout.addWidget(self.date_label)
        
        # Day
        self.day_label = QLabel("Monday")
        self.day_label.setFont(QFont('Arial', 16))
        self.day_label.setAlignment(Qt.AlignCenter)
        self.day_label.setStyleSheet(f"color: {COLORS['text_secondary']}; background: transparent;")
        main_layout.addWidget(self.day_label)
        
        main_layout.addStretch()
        
        # Hint
        hint_label = QLabel('🔄 Rotate to select • Press to confirm')
        hint_label.setFont(QFont('Arial', 11))
        hint_label.setAlignment(Qt.AlignCenter)
        hint_label.setStyleSheet(f"color: {COLORS['text_secondary']}; background: transparent;")
        main_layout.addWidget(hint_label)
        
        self.setLayout(main_layout)
        self.update_button_styles()
    
    def select_button(self, button_index):
        """Select button by index (0=settings, 1=emergency)"""
        self.selected_button = button_index
        self.update_button_styles()
    
    def update_button_styles(self):
        """Update button appearance based on selection"""
        if self.selected_button == 0:
            # Settings selected
            self.settings_button.setStyleSheet('''QPushButton {
    background-color: ''' + COLORS['cyan'] + ''';
    color: ''' + COLORS['bg'] + ''';
    border: 3px solid #FFFFFF;
    padding: 8px 12px;
    border-radius: 6px;
    font-weight: bold;
}''')
            self.emergency_button.setStyleSheet('''QPushButton {
    background-color: ''' + COLORS['primary'] + ''';
    color: ''' + COLORS['text_primary'] + ''';
    border: none;
    padding: 8px 12px;
    border-radius: 6px;
    font-weight: bold;
}''')
        else:
            # Emergency selected
            self.emergency_button.setStyleSheet('''QPushButton {
    background-color: ''' + COLORS['emergency'] + ''';
    color: #FFFFFF;
    border: 3px solid #FFFFFF;
    padding: 8px 12px;
    border-radius: 6px;
    font-weight: bold;
}''')
            self.settings_button.setStyleSheet('''QPushButton {
    background-color: ''' + COLORS['primary'] + ''';
    color: ''' + COLORS['text_primary'] + ''';
    border: none;
    padding: 8px 12px;
    border-radius: 6px;
    font-weight: bold;
}''')

class VoiceScreen(QWidget):
    """Voice assistant screen"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 15, 10, 20)
        main_layout.setSpacing(10)
        
        # Header
        header_container = QVBoxLayout()
        header_container.setSpacing(5)
        
        top_row = QHBoxLayout()
        top_row.setSpacing(8)
        
        self.time_label = QLabel("16:45")
        self.time_label.setFont(QFont('Arial', 16, QFont.Bold))
        self.time_label.setStyleSheet(f"color: {COLORS['accent']}; background: transparent;")
        top_row.addWidget(self.time_label)
        
        sep1 = QLabel("•")
        sep1.setFont(QFont('Arial', 13))
        sep1.setStyleSheet(f"color: {COLORS['text_secondary']}; background: transparent;")
        top_row.addWidget(sep1)
        
        self.date_label = QLabel("3rd Nov")
        self.date_label.setFont(QFont('Arial', 12))
        self.date_label.setStyleSheet(f"color: {COLORS['text_secondary']}; background: transparent;")
        top_row.addWidget(self.date_label)
        
        sep2 = QLabel("•")
        sep2.setFont(QFont('Arial', 13))
        sep2.setStyleSheet(f"color: {COLORS['text_secondary']}; background: transparent;")
        top_row.addWidget(sep2)
        
        self.day_label = QLabel("Monday")
        self.day_label.setFont(QFont('Arial', 12))
        self.day_label.setStyleSheet(f"color: {COLORS['text_secondary']}; background: transparent;")
        top_row.addWidget(self.day_label)
        
        top_row.addStretch()
        
        self.listening_indicator = VoiceListeningIndicator()
        top_row.addWidget(self.listening_indicator)
        
        status_label = QLabel("LISTENING")
        status_label.setFont(QFont('Arial', 9, QFont.Bold))
        status_label.setStyleSheet(f"color: {COLORS['cyan']}; background: transparent;")
        top_row.addWidget(status_label)
        
        header_container.addLayout(top_row)
        
        weather_row = QHBoxLayout()
        weather_row.setSpacing(8)
        
        self.weather_desc_label = QLabel("Loading")
        self.weather_desc_label.setFont(QFont('Arial', 11))
        self.weather_desc_label.setStyleSheet(f"color: {COLORS['text_secondary']}; background: transparent;")
        weather_row.addWidget(self.weather_desc_label)
        
        self.temp_label = QLabel("--°C")
        self.temp_label.setFont(QFont('Arial', 12, QFont.Bold))
        self.temp_label.setStyleSheet(f"color: {COLORS['accent']}; background: transparent;")
        weather_row.addWidget(self.temp_label)
        
        weather_row.addStretch()
        
        header_container.addLayout(weather_row)
        
        main_layout.addLayout(header_container)
        
        # Animated speaker
        speaker_container = QVBoxLayout()
        speaker_container.setAlignment(Qt.AlignCenter)
        speaker_container.addStretch()
        
        self.animated_speaker = AnimatedSpeaker()
        speaker_container.addWidget(self.animated_speaker, alignment=Qt.AlignCenter)
        
        speaker_container.addSpacing(20)
        
        self.status_text = QLabel("Listening...")
        self.status_text.setFont(QFont('Arial', 18, QFont.Bold))
        self.status_text.setAlignment(Qt.AlignCenter)
        self.status_text.setStyleSheet(f"color: {COLORS['cyan']}; background: transparent;")
        speaker_container.addWidget(self.status_text)
        
        speaker_container.addSpacing(10)
        
        self.subtitle_text = QLabel("How can I help you?")
        self.subtitle_text.setFont(QFont('Arial', 14))
        self.subtitle_text.setAlignment(Qt.AlignCenter)
        self.subtitle_text.setStyleSheet(f"color: {COLORS['text_secondary']}; background: transparent;")
        speaker_container.addWidget(self.subtitle_text)
        
        speaker_container.addStretch()
        
        main_layout.addLayout(speaker_container)
        
        # Back button
        back_button = QPushButton("← Back to Clock")
        back_button.setFont(QFont('Arial', 11))
        back_button.setStyleSheet('''QPushButton {
    background-color: ''' + COLORS['primary'] + ''';
    color: ''' + COLORS['text_primary'] + ''';
    border: none;
    padding: 10px 20px;
    border-radius: 6px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: ''' + COLORS['secondary'] + ''';
}''')
        self.back_button = back_button
        main_layout.addWidget(back_button)
        
        self.setLayout(main_layout)
    
    def start_listening(self):
        self.animated_speaker.start_speaking()
        self.status_text.setText("Listening...")
        self.subtitle_text.setText("How can I help you?")
    
    def stop_activity(self):
        self.animated_speaker.stop_speaking()
    
    def update_weather_display(self, temp, weather_desc):
        self.temp_label.setText(f"{temp}°C")
        self.weather_desc_label.setText(weather_desc)
    
    def update_day_display(self, day_str):
        self.day_label.setText(day_str)

class MonitoringDevice(QMainWindow):
    def __init__(self):
        super().__init__()
        self.brightness = 100
        self.volume = 50
        self.latitude = 6.8481
        self.longitude = 79.9267
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('Monitoring Device')
        self.setFixedSize(480, 800)
        self.setStyleSheet(f"background-color: {COLORS['bg']};")
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.stacked_widget = QStackedWidget()
        
        self.main_screen = MainScreen()
        self.voice_screen = VoiceScreen()
        
        self.voice_screen.back_button.clicked.connect(self.show_main_screen)
        
        self.stacked_widget.addWidget(self.main_screen)
        self.stacked_widget.addWidget(self.voice_screen)
        
        layout.addWidget(self.stacked_widget)
        central_widget.setLayout(layout)
        
        self.change_brightness(100)
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)
        self.update_time()
        
        self.weather_timer = QTimer()
        self.weather_timer.timeout.connect(self.update_weather)
        self.weather_timer.start(600000)
        self.update_weather()
        
        self.voice_activation_timer = QTimer()
        self.voice_activation_timer.timeout.connect(self.check_voice_activation)
        self.voice_activation_timer.start(100)
    
    def check_voice_activation(self):
        """Placeholder for voice detection - call self.trigger_voice_assistant() when 'Hi' detected"""
        pass
    
    def trigger_voice_assistant(self):
        """Activate voice assistant when 'Hi' is detected"""
        print("\n🎤 'Hi' detected! Activating Voice Assistant...")
        self.show_voice_screen()
    
    def show_main_screen(self):
        self.voice_screen.stop_activity()
        self.stacked_widget.setCurrentWidget(self.main_screen)
    
    def show_voice_screen(self):
        self.stacked_widget.setCurrentWidget(self.voice_screen)
        self.voice_screen.start_listening()
    
    def keyPressEvent(self, event):
        """Handle encoder button and rotation"""
        if self.stacked_widget.currentWidget() == self.main_screen:
            # Main screen - rotate to select button, press to activate
            if event.key() == Qt.Key_Space:
                # Space key - trigger voice UI
                print("\n🎤 Voice UI Activated! (Space pressed)\n")
                self.show_voice_screen()
                
            elif event.key() == Qt.Key_Left or event.key() == Qt.Key_Down:
                # Rotate CCW - select Settings
                self.main_screen.select_button(0)
                print("◄ Settings selected")
                
            elif event.key() == Qt.Key_Right or event.key() == Qt.Key_Up:
                # Rotate CW - select Emergency
                self.main_screen.select_button(1)
                print("Emergency selected ►")
                
            elif event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
                # Press - activate selected button
                if self.main_screen.selected_button == 0:
                    print("\n⚙️ Opening Settings...\n")
                    self.open_settings()
                else:
                    print("\n🚨 Emergency Call Activated!\n")
                    # Add emergency call functionality here
                    
        elif self.stacked_widget.currentWidget() == self.voice_screen:
            if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
                print("← Returning to Main Screen\n")
                self.show_main_screen()
    
    def open_settings(self):
        dialog = SettingsDialog(self)
        dialog.exec_()
        
    def change_brightness(self, value):
        effect = QGraphicsOpacityEffect()
        effect.setOpacity(value / 100.0)
        self.centralWidget().setGraphicsEffect(effect)
        self.brightness = value
    
    def change_volume(self, value):
        self.volume = value
        
    def update_weather(self):
        try:
            OPENWEATHERMAP_API_KEY = '382dd53601c32ec38ae0b61dad890a10'
            url = f"https://api.openweathermap.org/data/2.5/weather?lat={self.latitude}&lon={self.longitude}&appid={OPENWEATHERMAP_API_KEY}&units=metric"
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                temp = data['main']['temp']
                weather_desc = data['weather'][0]['description'].capitalize()
                
                if temp is not None:
                    self.main_screen.temp_widget.update_weather(round(temp), weather_desc)
                    self.voice_screen.update_weather_display(round(temp), weather_desc)
                else:
                    self.main_screen.temp_widget.update_weather("--", "No data")
                    self.voice_screen.update_weather_display("--", "No data")
            else:
                self.main_screen.temp_widget.update_weather("--", f"API Error")
                self.voice_screen.update_weather_display("--", f"API Error")
        
        except Exception as e:
            self.main_screen.temp_widget.update_weather("--", "Error")
            self.voice_screen.update_weather_display("--", "Error")
   
    def update_time(self):
        now = datetime.now()
        
        time_str = now.strftime("%H:%M")
        self.main_screen.time_label.setText(time_str)
        self.voice_screen.time_label.setText(time_str)
        
        day = now.day
        if 4 <= day <= 20 or 24 <= day <= 30:
            suffix = "th"
        else:
            suffix = ["st", "nd", "rd"][day % 10 - 1]
        
        date_str = f"{day}{suffix} of {now.strftime('%B %Y')}"
        self.main_screen.date_label.setText(date_str)
        
        compact_date = now.strftime(f"{day}{suffix} %b")
        self.voice_screen.date_label.setText(compact_date)
        
        day_str = now.strftime("%A")
        self.main_screen.day_label.setText(day_str)
        self.voice_screen.update_day_display(day_str)

def main():
    app = QApplication(sys.argv)
    window = MonitoringDevice()
    window.show()
    
    print("\n" + "="*75)
    print("           ROTARY ENCODER MONITORING DEVICE")
    print("="*75)
    print("\n📍 MAIN SCREEN:")
    print("  1. Rotate           → Highlight Settings or Emergency")
    print("  2. Press Enter      → Open highlighted button")
    print("  3. Press Space      → Open Voice UI (2nd screen)")
    print("\n⚙️  SETTINGS DIALOG:")
    print("  1. Rotate           → Cycle through: Brightness → Volume → Close")
    print("  2. Press Enter      → Activate (edit or close)")
    print("  3. While editing:")
    print("     - Rotate         → Adjust value ±5%")
    print("     - Press Enter    → Save and return to selection")
    print("\n📊 THREE OPTIONS IN SETTINGS:")
    print("  1. Brightness       → Edit screen brightness")
    print("  2. Volume           → Edit sound volume")
    print("  3. Close Settings   → Exit dialog (replaces ESC)")
    print("\n🎨 VISUAL STATES:")
    print("  Gray box (2px)      = Not selected")
    print("  Cyan box (3px)      = Brightness/Volume highlighted")
    print("  Red box (3px)       = Close button highlighted")
    print("  Green box (4px)     = Editing mode")
    print("\n🎤 VOICE UI (2nd Screen):")
    print("  Press Space         → Open from main screen")
    print("  Press Enter         → Return to main screen")
    print("\n⌨️  Keyboard Mapping:")
    print("  ← ↓ → ↑ = Rotate encoder")
    print("  Enter   = Press encoder button")
    print("  Space   = Trigger voice UI")
    print("="*75 + "\n")
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()