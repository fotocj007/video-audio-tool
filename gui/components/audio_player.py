#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
音频播放器组件
提供音频播放控制功能
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QSlider, QGroupBox, QMessageBox
)
from PySide6.QtCore import Qt, QTimer, QProcess
import os


class AudioPlayerWidget(QWidget):
    """音频播放器控件"""
    
    def __init__(self, prefix="player", parent=None):
        super().__init__(parent)
        self.prefix = prefix
        self.is_playing = False
        self.current_position = 0
        self.audio_duration = 0
        self.current_audio_file = None
        self.player_process = None
        
        # 创建定时器用于更新播放进度
        self.position_timer = QTimer()
        self.position_timer.timeout.connect(self.update_position)
        
        self.init_ui()
        
    def init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout(self)
        
        # 播放进度条
        progress_layout = QHBoxLayout()
        self.position_label = QLabel("00:00")
        progress_layout.addWidget(self.position_label)
        
        self.progress_slider = QSlider(Qt.Horizontal)
        self.progress_slider.setMinimum(0)
        self.progress_slider.setMaximum(100)
        self.progress_slider.setValue(0)
        self.progress_slider.sliderPressed.connect(self.on_progress_slider_pressed)
        self.progress_slider.sliderReleased.connect(self.on_progress_slider_released)
        progress_layout.addWidget(self.progress_slider)
        
        self.duration_label = QLabel("00:00")
        progress_layout.addWidget(self.duration_label)
        
        layout.addLayout(progress_layout)
        
        # 播放按钮组
        button_layout = QHBoxLayout()
        
        self.play_pause_btn = QPushButton("播放")
        self.play_pause_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 8px 16px;
                font-size: 12px;
                border-radius: 4px;
                min-width: 60px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        self.play_pause_btn.clicked.connect(self.toggle_play_pause)
        self.play_pause_btn.setEnabled(False)
        button_layout.addWidget(self.play_pause_btn)
        
        self.stop_btn = QPushButton("停止")
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 8px 16px;
                font-size: 12px;
                border-radius: 4px;
                min-width: 60px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        self.stop_btn.clicked.connect(self.stop_playback)
        self.stop_btn.setEnabled(False)
        button_layout.addWidget(self.stop_btn)
        
        # 音量控制
        volume_layout = QHBoxLayout()
        volume_layout.addWidget(QLabel("音量:"))
        
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(50)
        self.volume_slider.setMaximumWidth(150)
        self.volume_slider.valueChanged.connect(self.update_volume_label)
        volume_layout.addWidget(self.volume_slider)
        
        self.volume_label = QLabel("50%")
        self.volume_label.setMinimumWidth(35)
        volume_layout.addWidget(self.volume_label)
        
        button_layout.addLayout(volume_layout)
        layout.addLayout(button_layout)
        
    def set_audio_file(self, file_path, audio_info):
        """设置音频文件"""
        try:
            # 设置音频时长
            duration = audio_info.get('duration', 0)
            self.audio_duration = duration
            
            self.duration_label.setText(self.format_time(duration))
            self.progress_slider.setMaximum(int(duration))
            
            # 启用播放控件
            self.play_pause_btn.setEnabled(True)
            self.stop_btn.setEnabled(True)
            
            # 存储当前文件路径
            self.current_audio_file = file_path
            
        except Exception as e:
            print(f"设置音频文件失败: {str(e)}")
            
    def toggle_play_pause(self):
        """切换播放/暂停状态"""
        if not self.current_audio_file:
            return
            
        if self.is_playing:
            self.pause_playback()
        else:
            self.start_playback()
            
    def start_playback(self):
        """开始播放音频"""
        if not self.current_audio_file:
            return
            
        try:
            # 停止之前的播放进程
            if self.player_process is not None and self.player_process.state() == QProcess.Running:
                self.player_process.kill()
                
            # 获取ffplay.exe路径
            ffplay_path = os.path.join(os.getcwd(), "ffplay.exe")
            if not os.path.exists(ffplay_path):
                QMessageBox.warning(self, "错误", "找不到ffplay.exe文件")
                return
                
            # 创建播放进程
            self.player_process = QProcess()
            self.player_process.finished.connect(self.on_playback_finished)
            
            # 设置ffplay参数
            volume = self.volume_slider.value() / 100.0
            args = [
                "-nodisp",  # 不显示视频窗口
                "-autoexit",  # 播放完成后自动退出
                "-volume", str(int(volume * 100)),  # 设置音量
                self.current_audio_file
            ]
            
            self.player_process.start(ffplay_path, args)
            
            if self.player_process.waitForStarted():
                self.is_playing = True
                self.play_pause_btn.setText("暂停")
                
                # 启动进度更新定时器
                self.position_timer.start(1000)  # 每秒更新一次进度
            else:
                QMessageBox.warning(self, "错误", "无法启动音频播放")
                
        except Exception as e:
            QMessageBox.critical(self, "播放错误", f"播放音频时发生错误: {str(e)}")
            
    def pause_playback(self):
        """暂停播放"""
        if self.player_process is not None and self.player_process.state() == QProcess.Running:
            self.player_process.kill()
            
        self.is_playing = False
        self.play_pause_btn.setText("播放")
        self.position_timer.stop()
        
    def stop_playback(self):
        """停止播放"""
        if self.player_process is not None and self.player_process.state() == QProcess.Running:
            self.player_process.kill()
            
        self.is_playing = False
        self.current_position = 0
        
        self.play_pause_btn.setText("播放")
        self.progress_slider.setValue(0)
        self.position_label.setText("00:00")
        self.position_timer.stop()
        
    def on_playback_finished(self):
        """播放完成回调"""
        self.is_playing = False
        self.current_position = 0
        
        self.play_pause_btn.setText("播放")
        self.progress_slider.setValue(0)
        self.position_label.setText("00:00")
        self.position_timer.stop()
        
    def update_position(self):
        """更新播放进度"""
        if self.is_playing and self.audio_duration > 0:
            self.current_position += 1
            
            if self.current_position <= self.audio_duration:
                self.progress_slider.setValue(int(self.current_position))
                self.position_label.setText(self.format_time(self.current_position))
            else:
                # 播放完成
                self.on_playback_finished()
                
    def on_progress_slider_pressed(self):
        """进度条被按下"""
        self.position_timer.stop()
        
    def on_progress_slider_released(self):
        """进度条被释放"""
        if self.is_playing:
            # 重新开始播放（简化实现，实际应该支持跳转）
            self.current_position = self.progress_slider.value()
            self.position_timer.start(1000)
            
    def update_volume_label(self, volume):
        """更新音量标签"""
        self.volume_label.setText(f"{volume}%")
        
    def format_time(self, seconds):
        """格式化时间显示"""
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"
        
    def reset(self):
        """重置播放器状态"""
        self.stop_playback()
        self.current_audio_file = None
        self.audio_duration = 0
        self.play_pause_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
        self.duration_label.setText("00:00")
        self.progress_slider.setMaximum(100)