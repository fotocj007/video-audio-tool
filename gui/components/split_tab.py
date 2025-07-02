#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
音频拆分标签页组件
实现音频拆分功能的用户界面
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QLineEdit, QListWidget, QProgressBar, QFileDialog,
    QMessageBox, QGroupBox
)
from PySide6.QtCore import Qt
import os
from core.audio_handler import AudioHandler
from .audio_player import AudioPlayerWidget


class SplitTabWidget(QWidget):
    """音频拆分标签页"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.audio_handler = AudioHandler()
        self.split_file_path = None
        self.output_dir = None
        self.split_worker = None
        
        self.init_ui()
        
    def init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout(self)
        
        # 文件选择组
        file_group = QGroupBox("选择音频文件")
        file_layout = QHBoxLayout(file_group)
        
        self.file_label = QLabel("未选择文件")
        self.file_label.setStyleSheet("QLabel { padding: 5px; border: 1px solid #ccc; }")
        file_layout.addWidget(self.file_label)
        
        browse_btn = QPushButton("浏览")
        browse_btn.clicked.connect(self.browse_audio_file)
        file_layout.addWidget(browse_btn)
        
        layout.addWidget(file_group)
        
        # 音频信息显示
        self.audio_info_label = QLabel("音频信息: 未选择文件")
        self.audio_info_label.setStyleSheet("QLabel { color: #666; font-size: 12px; padding: 5px; }")
        layout.addWidget(self.audio_info_label)
        
        # 音频播放控件
        self.audio_player = AudioPlayerWidget("split", self)
        player_group = QGroupBox("音频播放控制")
        player_layout = QVBoxLayout(player_group)
        player_layout.addWidget(self.audio_player)
        layout.addWidget(player_group)
        
        # 时间点管理组
        time_group = QGroupBox("拆分时间点管理")
        time_layout = QVBoxLayout(time_group)
        
        # 添加时间点
        add_time_layout = QHBoxLayout()
        add_time_layout.addWidget(QLabel("时间点 (HH:MM:SS):"))
        
        self.time_input = QLineEdit()
        self.time_input.setPlaceholderText("例如: 00:01:30")
        add_time_layout.addWidget(self.time_input)
        
        add_time_btn = QPushButton("添加时间点")
        add_time_btn.clicked.connect(self.add_time_point)
        add_time_layout.addWidget(add_time_btn)
        
        time_layout.addLayout(add_time_layout)
        
        # 时间点列表
        self.time_list = QListWidget()
        self.time_list.setMaximumHeight(150)
        time_layout.addWidget(self.time_list)
        
        # 删除时间点按钮
        remove_time_btn = QPushButton("删除选中时间点")
        remove_time_btn.clicked.connect(self.remove_time_point)
        time_layout.addWidget(remove_time_btn)
        
        layout.addWidget(time_group)
        
        # 输出设置组
        output_group = QGroupBox("输出设置")
        output_layout = QHBoxLayout(output_group)
        
        output_layout.addWidget(QLabel("输出目录:"))
        self.output_label = QLabel("未选择目录")
        self.output_label.setStyleSheet("QLabel { padding: 5px; border: 1px solid #ccc; }")
        output_layout.addWidget(self.output_label)
        
        output_btn = QPushButton("选择目录")
        output_btn.clicked.connect(self.browse_output_dir)
        output_layout.addWidget(output_btn)
        
        layout.addWidget(output_group)
        
        # 进度条和开始按钮
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)
        
        start_btn = QPushButton("开始拆分")
        start_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border: none;
                padding: 10px;
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
        """)
        start_btn.clicked.connect(self.start_split)
        layout.addWidget(start_btn)
        
        layout.addStretch()
        
    def browse_audio_file(self):
        """浏览音频文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择音频文件", "", 
            "音频文件 (*.mp3 *.wav *.m4a *.flac *.aac *.ogg)")
        if file_path:
            self.file_label.setText(os.path.basename(file_path))
            self.split_file_path = file_path
            self.update_audio_info(file_path)
            
    def browse_output_dir(self):
        """浏览输出目录"""
        dir_path = QFileDialog.getExistingDirectory(self, "选择输出目录")
        if dir_path:
            self.output_label.setText(dir_path)
            self.output_dir = dir_path
            
    def update_audio_info(self, file_path):
        """更新音频信息"""
        try:
            audio_info = self.audio_handler.get_audio_info(file_path)
            if audio_info.get('success', False):
                info_text = f"音频信息: 时长 {audio_info['duration_str']} | {audio_info['channels_str']} | {audio_info['sample_rate_str']}"
                self.audio_info_label.setText(info_text)
                self.audio_info_label.setStyleSheet("QLabel { color: #333; font-size: 12px; padding: 5px; }")
                
                # 更新播放控件
                self.audio_player.set_audio_file(file_path, audio_info)
            else:
                error_msg = audio_info.get('error', '未知错误')
                self.audio_info_label.setText(f"获取音频信息失败: {error_msg}")
                self.audio_info_label.setStyleSheet("QLabel { color: #d32f2f; font-size: 12px; padding: 5px; }")
        except Exception as e:
            self.audio_info_label.setText(f"获取音频信息异常: {str(e)}")
            self.audio_info_label.setStyleSheet("QLabel { color: #d32f2f; font-size: 12px; padding: 5px; }")
            
    def add_time_point(self):
        """添加时间点"""
        time_text = self.time_input.text().strip()
        if time_text:
            # 验证时间格式
            if self.validate_time_format(time_text):
                # 检查是否已存在相同时间点
                existing_times = []
                for i in range(self.time_list.count()):
                    existing_times.append(self.time_list.item(i).text())
                
                if time_text not in existing_times:
                    self.time_list.addItem(time_text)
                    self.sort_time_points()
                    self.time_input.clear()
                else:
                    QMessageBox.warning(self, "重复时间点", "该时间点已存在")
            else:
                QMessageBox.warning(self, "格式错误", "请输入正确的时间格式 (HH:MM:SS)")
                
    def remove_time_point(self):
        """删除时间点"""
        current_row = self.time_list.currentRow()
        if current_row >= 0:
            self.time_list.takeItem(current_row)
            
    def sort_time_points(self):
        """对时间点列表进行排序"""
        # 获取所有时间点
        time_points = []
        for i in range(self.time_list.count()):
            time_points.append(self.time_list.item(i).text())
        
        # 按时间排序
        def time_to_seconds(time_str):
            parts = time_str.split(':')
            hours, minutes, seconds = map(int, parts)
            return hours * 3600 + minutes * 60 + seconds
        
        time_points.sort(key=time_to_seconds)
        
        # 清空列表并重新添加排序后的时间点
        self.time_list.clear()
        for time_point in time_points:
            self.time_list.addItem(time_point)
            
    def validate_time_format(self, time_str):
        """验证时间格式"""
        try:
            parts = time_str.split(':')
            if len(parts) != 3:
                return False
            hours, minutes, seconds = map(int, parts)
            return 0 <= hours <= 23 and 0 <= minutes <= 59 and 0 <= seconds <= 59
        except ValueError:
            return False
            
    def start_split(self):
        """开始音频拆分"""
        if not self.split_file_path:
            QMessageBox.warning(self, "错误", "请先选择音频文件")
            return
            
        if not self.output_dir:
            QMessageBox.warning(self, "错误", "请先选择输出目录")
            return
            
        if self.time_list.count() == 0:
            QMessageBox.warning(self, "错误", "请至少添加一个拆分时间点")
            return
            
        # 获取时间点列表
        time_points = []
        for i in range(self.time_list.count()):
            time_points.append(self.time_list.item(i).text())
            
        # 启动工作线程
        self.progress.setVisible(True)
        self.progress.setRange(0, 100)
        
        from gui.worker_threads import AudioWorkerThread
        
        self.split_worker = AudioWorkerThread(
            'split',
            audio_path=self.split_file_path,
            time_points=time_points,
            output_dir=self.output_dir
        )
        
        # 连接信号
        self.split_worker.progress_updated.connect(self.progress.setValue)
        self.split_worker.status_updated.connect(lambda msg: print(f"状态: {msg}"))
        self.split_worker.finished_successfully.connect(self.on_finished)
        self.split_worker.error_occurred.connect(self.on_error)
        
        # 启动线程
        self.split_worker.start()
        
    def on_finished(self, message):
        """拆分完成回调"""
        self.progress.setVisible(False)
        QMessageBox.information(self, "处理完成", message)
        
    def on_error(self, error_message):
        """拆分错误回调"""
        self.progress.setVisible(False)
        QMessageBox.critical(self, "处理错误", error_message)