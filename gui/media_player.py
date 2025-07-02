# -*- coding: utf-8 -*-
"""
媒体播放器组件
实现视频和音频播放功能
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QSlider, QLabel, QSizePolicy, QFrame
)
from PySide6.QtCore import Qt, QTimer, QUrl, Signal
from PySide6.QtGui import QPixmap, QPainter, QBrush, QColor
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget
import os

class MediaPlayerWidget(QWidget):
    """媒体播放器组件"""
    
    # 信号
    positionChanged = Signal(int)
    durationChanged = Signal(int)
    
    def __init__(self, player_type="video", compact=True):
        """
        初始化媒体播放器
        
        Args:
            player_type: 播放器类型 "video" 或 "audio"
            compact: 是否使用紧凑模式
        """
        super().__init__()
        self.player_type = player_type
        self.compact = compact
        self.current_file = None
        
        # 创建媒体播放器
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)
        
        # 连接信号
        self.media_player.positionChanged.connect(self.position_changed)
        self.media_player.durationChanged.connect(self.duration_changed)
        
        self.init_ui()
        
    def init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # 视频显示区域（仅视频播放器需要）
        if self.player_type == "video":
            self.video_widget = QVideoWidget()
            self.media_player.setVideoOutput(self.video_widget)
            
            # 设置9:16竖屏比例
            if self.compact:
                # 紧凑模式：减少播放器宽度
                video_width = 260
                video_height = int(video_width * 16 / 9)
                self.video_widget.setFixedSize(video_width, video_height)
            else:
                # 标准模式：减少播放器宽度
                video_width = 320
                video_height = int(video_width * 16 / 9)
                self.video_widget.setFixedSize(video_width, video_height)
                
            # 设置视频组件居中对齐
            self.video_widget.setStyleSheet("""
                QVideoWidget {
                    background-color: #000;
                    border: 1px solid #ccc;
                }
            """)
                
            layout.addWidget(self.video_widget, 0, Qt.AlignCenter)
        else:
            # 音频播放器显示音频信息
            self.audio_info_label = QLabel("未加载音频文件")
            self.audio_info_label.setAlignment(Qt.AlignCenter)
            self.audio_info_label.setStyleSheet("""
                QLabel {
                    background-color: #f0f0f0;
                    border: 2px dashed #ccc;
                    border-radius: 10px;
                    padding: 20px;
                    font-size: 14px;
                    color: #666;
                }
            """)
            if self.compact:
                self.audio_info_label.setMaximumHeight(80)
            else:
                self.audio_info_label.setMinimumHeight(120)
            layout.addWidget(self.audio_info_label)
        
        # 控制面板
        control_frame = QFrame()
        control_frame.setFrameStyle(QFrame.Box)
        control_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                padding: 3px;
                max-height: 80px;
            }
        """)
        control_layout = QVBoxLayout(control_frame)
        
        # 播放控制按钮
        button_layout = QHBoxLayout()
        
        self.play_button = QPushButton("▶")
        self.play_button.setFixedSize(35, 25)
        self.play_button.clicked.connect(self.toggle_play)
        self.play_button.setEnabled(False)
        button_layout.addWidget(self.play_button)
        
        self.stop_button = QPushButton("⏹")
        self.stop_button.setFixedSize(35, 25)
        self.stop_button.clicked.connect(self.stop)
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.stop_button)
        
        button_layout.addStretch()
        
        # 音量控制
        volume_label = QLabel("音量:")
        button_layout.addWidget(volume_label)
        
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(70)
        self.volume_slider.setMaximumWidth(100)
        self.volume_slider.valueChanged.connect(self.set_volume)
        button_layout.addWidget(self.volume_slider)
        
        control_layout.addLayout(button_layout)
        
        # 进度条
        progress_layout = QHBoxLayout()
        
        self.time_label = QLabel("00:00 / 00:00")
        self.time_label.setMinimumWidth(100)
        progress_layout.addWidget(self.time_label)
        
        self.position_slider = QSlider(Qt.Horizontal)
        self.position_slider.setRange(0, 0)
        self.position_slider.sliderMoved.connect(self.set_position)
        progress_layout.addWidget(self.position_slider)
        
        control_layout.addLayout(progress_layout)
        
        layout.addWidget(control_frame)
        
        # 设置初始音量
        self.set_volume(70)
        
    def load_media(self, file_path):
        """加载媒体文件"""
        if not os.path.exists(file_path):
            return False
            
        self.current_file = file_path
        self.media_player.setSource(QUrl.fromLocalFile(file_path))
        
        # 更新界面
        filename = os.path.basename(file_path)
        if self.player_type == "audio":
            self.audio_info_label.setText(f"音频文件: {filename}")
            
        # 启用控制按钮
        self.play_button.setEnabled(True)
        self.stop_button.setEnabled(True)
        
        return True
        
    def toggle_play(self):
        """切换播放/暂停状态"""
        if self.media_player.playbackState() == QMediaPlayer.PlayingState:
            self.media_player.pause()
            self.play_button.setText("▶")
        else:
            self.media_player.play()
            self.play_button.setText("⏸")
            
    def stop(self):
        """停止播放"""
        self.media_player.stop()
        self.play_button.setText("▶")
        
    def set_position(self, position):
        """设置播放位置"""
        self.media_player.setPosition(position)
        
    def set_volume(self, volume):
        """设置音量"""
        self.audio_output.setVolume(volume / 100.0)
        
    def position_changed(self, position):
        """播放位置改变"""
        self.position_slider.setValue(position)
        self.update_time_label(position, self.media_player.duration())
        self.positionChanged.emit(position)
        
    def duration_changed(self, duration):
        """播放时长改变"""
        self.position_slider.setRange(0, duration)
        self.update_time_label(self.media_player.position(), duration)
        self.durationChanged.emit(duration)
        
    def update_time_label(self, position, duration):
        """更新时间标签"""
        def format_time(ms):
            seconds = ms // 1000
            minutes = seconds // 60
            seconds = seconds % 60
            return f"{minutes:02d}:{seconds:02d}"
            
        current_time = format_time(position)
        total_time = format_time(duration)
        self.time_label.setText(f"{current_time} / {total_time}")
        
    def clear(self):
        """清空播放器"""
        self.media_player.stop()
        self.media_player.setSource(QUrl())
        self.current_file = None
        
        if self.player_type == "audio":
            self.audio_info_label.setText("未加载音频文件")
            
        self.play_button.setEnabled(False)
        self.stop_button.setEnabled(False)
        self.play_button.setText("▶")
        self.position_slider.setValue(0)
        self.time_label.setText("00:00 / 00:00")

class CompactVideoPlayer(MediaPlayerWidget):
    """紧凑型视频播放器"""
    
    def __init__(self):
        super().__init__(player_type="video", compact=True)
        
class CompactAudioPlayer(MediaPlayerWidget):
    """紧凑型音频播放器"""
    
    def __init__(self):
        super().__init__(player_type="audio", compact=True)