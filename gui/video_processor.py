#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视频处理模块GUI
实现视频拆分、提取音频、合成视频等功能的用户界面
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QPushButton, QLabel, QLineEdit, QListWidget, QComboBox,
    QCheckBox, QTextEdit, QProgressBar, QFileDialog,
    QMessageBox, QGroupBox, QGridLayout, QSpacerItem,
    QSizePolicy
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont
import os

from core import VideoHandler, VIDEO_HANDLER_AVAILABLE
from gui.worker_threads import VideoWorkerThread
from gui.media_player import CompactVideoPlayer, CompactAudioPlayer

class VideoProcessorWidget(QWidget):
    """视频处理主窗口部件"""
    
    def __init__(self):
        super().__init__()
        print(f"VIDEO_HANDLER_AVAILABLE: {VIDEO_HANDLER_AVAILABLE}")
        print(f"VideoHandler: {VideoHandler}")
        
        if VIDEO_HANDLER_AVAILABLE and VideoHandler:
            try:
                self.video_handler = VideoHandler()
                print("✓ VideoHandler 初始化成功")
            except Exception as e:
                print(f"✗ VideoHandler 初始化失败: {e}")
                self.video_handler = None
        else:
            print("✗ VideoHandler 不可用")
            self.video_handler = None
        self.init_ui()
        
    def init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout(self)
        
        # 创建标签页
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)
        
        # 视频拆分标签页
        self.split_tab = self.create_split_tab()
        tab_widget.addTab(self.split_tab, "视频拆分")
        
        # 提取音频标签页
        self.extract_tab = self.create_extract_tab()
        tab_widget.addTab(self.extract_tab, "提取音频")
        
        # 合成视频标签页
        self.merge_tab = self.create_merge_tab()
        tab_widget.addTab(self.merge_tab, "合成视频")
        
    def create_split_tab(self):
        """创建视频拆分标签页"""
        widget = QWidget()
        main_layout = QHBoxLayout(widget)
        
        # 左侧：视频播放器
        self.split_video_player = CompactVideoPlayer()
        main_layout.addWidget(self.split_video_player, 2)
        
        # 右侧：控制面板
        right_panel = QWidget()
        layout = QVBoxLayout(right_panel)
        
        # 文件选择组
        file_group = QGroupBox("选择视频文件")
        file_layout = QVBoxLayout(file_group)
        
        # 文件选择行
        file_select_layout = QHBoxLayout()
        self.split_file_label = QLabel("未选择文件")
        self.split_file_label.setStyleSheet("QLabel { padding: 5px; border: 1px solid #ccc; }")
        file_select_layout.addWidget(self.split_file_label)
        
        split_browse_btn = QPushButton("浏览")
        split_browse_btn.clicked.connect(self.browse_video_file_for_split)
        file_select_layout.addWidget(split_browse_btn)
        
        file_layout.addLayout(file_select_layout)
        
        # 视频信息显示
        self.split_video_info_label = QLabel("")
        self.split_video_info_label.setStyleSheet("QLabel { padding: 5px; color: #666; font-size: 12px; }")
        self.split_video_info_label.setVisible(False)
        file_layout.addWidget(self.split_video_info_label)
        
        layout.addWidget(file_group)
        
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
        self.split_output_label = QLabel("未选择目录")
        self.split_output_label.setStyleSheet("QLabel { padding: 5px; border: 1px solid #ccc; }")
        output_layout.addWidget(self.split_output_label)
        
        split_output_btn = QPushButton("选择目录")
        split_output_btn.clicked.connect(self.browse_output_dir_for_split)
        output_layout.addWidget(split_output_btn)
        
        layout.addWidget(output_group)
        
        # 进度条和开始按钮
        self.split_progress = QProgressBar()
        self.split_progress.setVisible(False)
        layout.addWidget(self.split_progress)
        
        start_split_btn = QPushButton("开始拆分")
        start_split_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px;
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        start_split_btn.clicked.connect(self.start_video_split)
        layout.addWidget(start_split_btn)
        
        layout.addStretch()
        
        # 将右侧面板添加到主布局
        main_layout.addWidget(right_panel, 2)
        
        return widget
        
    def create_extract_tab(self):
        """创建提取音频标签页"""
        widget = QWidget()
        main_layout = QHBoxLayout(widget)
        
        # 左侧：视频播放器
        self.extract_video_player = CompactVideoPlayer()
        main_layout.addWidget(self.extract_video_player, 1)
        
        # 右侧：控制面板
        right_panel = QWidget()
        layout = QVBoxLayout(right_panel)
        
        # 文件选择组
        file_group = QGroupBox("选择视频文件")
        file_layout = QVBoxLayout(file_group)
        
        # 文件选择行
        file_select_layout = QHBoxLayout()
        self.extract_file_label = QLabel("未选择文件")
        self.extract_file_label.setStyleSheet("QLabel { padding: 5px; border: 1px solid #ccc; }")
        file_select_layout.addWidget(self.extract_file_label)
        
        extract_browse_btn = QPushButton("浏览")
        extract_browse_btn.clicked.connect(self.browse_video_file_for_extract)
        file_select_layout.addWidget(extract_browse_btn)
        
        file_layout.addLayout(file_select_layout)
        
        # 视频信息显示
        self.extract_video_info_label = QLabel("")
        self.extract_video_info_label.setStyleSheet("QLabel { padding: 5px; color: #666; font-size: 12px; }")
        self.extract_video_info_label.setVisible(False)
        file_layout.addWidget(self.extract_video_info_label)
        
        layout.addWidget(file_group)
        
        # 输出设置组
        output_group = QGroupBox("输出设置")
        output_layout = QGridLayout(output_group)
        
        output_layout.addWidget(QLabel("输出格式:"), 0, 0)
        self.audio_format_combo = QComboBox()
        self.audio_format_combo.addItems(["mp3", "wav", "aac"])
        output_layout.addWidget(self.audio_format_combo, 0, 1)
        
        output_layout.addWidget(QLabel("输出文件:"), 1, 0)
        self.extract_output_label = QLabel("未选择文件")
        self.extract_output_label.setStyleSheet("QLabel { padding: 5px; border: 1px solid #ccc; }")
        output_layout.addWidget(self.extract_output_label, 1, 1)
        
        extract_output_btn = QPushButton("选择保存位置")
        extract_output_btn.clicked.connect(self.browse_output_file_for_extract)
        output_layout.addWidget(extract_output_btn, 1, 2)
        
        layout.addWidget(output_group)
        
        # 进度条和开始按钮
        self.extract_progress = QProgressBar()
        self.extract_progress.setVisible(False)
        layout.addWidget(self.extract_progress)
        
        start_extract_btn = QPushButton("开始提取")
        start_extract_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 10px;
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        start_extract_btn.clicked.connect(self.start_audio_extract)
        layout.addWidget(start_extract_btn)
        
        layout.addStretch()
        
        # 将右侧面板添加到主布局
        main_layout.addWidget(right_panel, 2)
        
        return widget
        
    def create_merge_tab(self):
        """创建合成视频标签页"""
        widget = QWidget()
        main_layout = QHBoxLayout(widget)
        
        # 左侧：主播放器
        self.merge_main_player = CompactVideoPlayer()
        main_layout.addWidget(self.merge_main_player, 1)
        
        # 右侧：控制面板
        right_panel = QWidget()
        layout = QVBoxLayout(right_panel)
        
        # 视频文件选择组
        video_group = QGroupBox("选择视频文件")
        video_layout = QVBoxLayout(video_group)
        
        # 文件选择行
        video_select_layout = QHBoxLayout()
        self.merge_video_label = QLabel("未选择文件")
        self.merge_video_label.setStyleSheet("QLabel { padding: 5px; border: 1px solid #ccc; }")
        video_select_layout.addWidget(self.merge_video_label)
        
        merge_video_btn = QPushButton("浏览")
        merge_video_btn.clicked.connect(self.browse_video_file_for_merge)
        video_select_layout.addWidget(merge_video_btn)
        
        # 播放视频按钮
        self.play_video_btn = QPushButton("播放视频")
        self.play_video_btn.clicked.connect(self.play_selected_video)
        self.play_video_btn.setEnabled(False)
        video_select_layout.addWidget(self.play_video_btn)
        
        video_layout.addLayout(video_select_layout)
        
        # 视频信息显示
        self.merge_video_info_label = QLabel("")
        self.merge_video_info_label.setStyleSheet("QLabel { padding: 5px; color: #666; font-size: 12px; }")
        self.merge_video_info_label.setVisible(False)
        video_layout.addWidget(self.merge_video_info_label)
        
        layout.addWidget(video_group)
        
        # 音频文件选择组
        audio_group = QGroupBox("选择音频文件")
        audio_layout = QVBoxLayout(audio_group)
        
        audio_select_layout = QHBoxLayout()
        self.merge_audio_label = QLabel("未选择文件")
        self.merge_audio_label.setStyleSheet("QLabel { padding: 5px; border: 1px solid #ccc; }")
        audio_select_layout.addWidget(self.merge_audio_label)
        
        merge_audio_btn = QPushButton("浏览")
        merge_audio_btn.clicked.connect(self.browse_audio_file_for_merge)
        audio_select_layout.addWidget(merge_audio_btn)
        
        # 播放音频按钮
        self.play_audio_btn = QPushButton("播放音频")
        self.play_audio_btn.clicked.connect(self.play_selected_audio)
        self.play_audio_btn.setEnabled(False)
        audio_select_layout.addWidget(self.play_audio_btn)
        
        audio_layout.addLayout(audio_select_layout)
        layout.addWidget(audio_group)
        
        # 选项设置组
        options_group = QGroupBox("合成选项")
        options_layout = QVBoxLayout(options_group)
        
        self.replace_audio_checkbox = QCheckBox("替换视频原有声音")
        self.replace_audio_checkbox.setChecked(True)
        options_layout.addWidget(self.replace_audio_checkbox)
        
        layout.addWidget(options_group)
        
        # 输出设置组
        output_group = QGroupBox("输出设置")
        output_layout = QVBoxLayout(output_group)
        
        # 输出文件选择
        output_file_layout = QHBoxLayout()
        output_file_layout.addWidget(QLabel("输出文件:"))
        self.merge_output_label = QLabel("未选择文件")
        self.merge_output_label.setStyleSheet("QLabel { padding: 5px; border: 1px solid #ccc; }")
        output_file_layout.addWidget(self.merge_output_label)
        
        merge_output_btn = QPushButton("选择保存位置")
        merge_output_btn.clicked.connect(self.browse_output_file_for_merge)
        output_file_layout.addWidget(merge_output_btn)
        
        # 播放合成视频按钮
        self.play_merged_btn = QPushButton("播放合成视频")
        self.play_merged_btn.clicked.connect(self.play_merged_video)
        self.play_merged_btn.setEnabled(False)
        output_file_layout.addWidget(self.play_merged_btn)
        
        output_layout.addLayout(output_file_layout)
        
        layout.addWidget(output_group)
        
        # 进度条和开始按钮
        self.merge_progress = QProgressBar()
        self.merge_progress.setVisible(False)
        layout.addWidget(self.merge_progress)
        
        start_merge_btn = QPushButton("开始合成")
        start_merge_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 10px;
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        start_merge_btn.clicked.connect(self.start_video_merge)
        layout.addWidget(start_merge_btn)
        
        layout.addStretch()
        
        # 将右侧面板添加到主布局
        main_layout.addWidget(right_panel, 1)
        
        return widget
        
    # 文件浏览方法
    def browse_video_file_for_split(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择视频文件", "", 
            "视频文件 (*.mp4 *.avi *.mov *.mkv *.wmv)")
        if file_path:
            self.split_file_label.setText(os.path.basename(file_path))
            self.split_file_path = file_path
            self._update_video_info_for_split(file_path)
            # 加载视频到播放器
            self.split_video_player.load_media(file_path)
    
    def _update_video_info_for_split(self, file_path):
        """更新视频拆分页面的视频信息显示"""
        if self.video_handler:
            try:
                info = self.video_handler.get_video_info(file_path)
                # 调试信息：检查返回值类型
                if not isinstance(info, dict):
                    self.split_video_info_label.setText(f"返回值类型错误: {type(info)}")
                    self.split_video_info_label.setVisible(True)
                    return
                    
                if info.get('success', False):
                    info_text = f"时长: {info['duration_str']} | 分辨率: {info['size_str']} | 帧率: {info['fps']:.1f}fps"
                    self.split_video_info_label.setText(info_text)
                    self.split_video_info_label.setVisible(True)
                else:
                    error_msg = info.get('error', '未知错误')
                    self.split_video_info_label.setText(f"获取视频信息失败: {error_msg}")
                    self.split_video_info_label.setVisible(True)
            except Exception as e:
                import traceback
                error_detail = traceback.format_exc()
                self.split_video_info_label.setText(f"获取视频信息出错: {str(e)}")
                self.split_video_info_label.setVisible(True)
                print(f"视频信息获取错误详情: {error_detail}")
        else:
            self.split_video_info_label.setText("视频处理功能不可用")
            self.split_video_info_label.setVisible(True)
            
    def browse_video_file_for_extract(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择视频文件", "", 
            "视频文件 (*.mp4 *.avi *.mov *.mkv *.wmv)")
        if file_path:
            self.extract_file_label.setText(os.path.basename(file_path))
            self.extract_file_path = file_path
            self._update_video_info_for_extract(file_path)
            # 加载视频到播放器
            self.extract_video_player.load_media(file_path)
    
    def _update_video_info_for_extract(self, file_path):
        """更新音频提取页面的视频信息显示"""
        if self.video_handler:
            try:
                info = self.video_handler.get_video_info(file_path)
                # 调试信息：检查返回值类型
                if not isinstance(info, dict):
                    self.extract_video_info_label.setText(f"返回值类型错误: {type(info)}")
                    self.extract_video_info_label.setVisible(True)
                    return
                    
                if info.get('success', False):
                    info_text = f"时长: {info['duration_str']} | 分辨率: {info['size_str']} | 帧率: {info['fps']:.1f}fps"
                    self.extract_video_info_label.setText(info_text)
                    self.extract_video_info_label.setVisible(True)
                else:
                    error_msg = info.get('error', '未知错误')
                    self.extract_video_info_label.setText(f"获取视频信息失败: {error_msg}")
                    self.extract_video_info_label.setVisible(True)
            except Exception as e:
                import traceback
                error_detail = traceback.format_exc()
                self.extract_video_info_label.setText(f"获取视频信息出错: {str(e)}")
                self.extract_video_info_label.setVisible(True)
                print(f"视频信息获取错误详情: {error_detail}")
        else:
            self.extract_video_info_label.setText("视频处理功能不可用")
            self.extract_video_info_label.setVisible(True)
            
    def browse_video_file_for_merge(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择视频文件", "", 
            "视频文件 (*.mp4 *.avi *.mov *.mkv *.wmv)")
        if file_path:
            self.merge_video_label.setText(os.path.basename(file_path))
            self.merge_video_path = file_path
            self._update_video_info_for_merge(file_path)
            # 启用播放视频按钮
            self.play_video_btn.setEnabled(True)
    
    def _update_video_info_for_merge(self, file_path):
        """更新视频合并页面的视频信息显示"""
        if self.video_handler:
            try:
                info = self.video_handler.get_video_info(file_path)
                # 调试信息：检查返回值类型
                if not isinstance(info, dict):
                    self.merge_video_info_label.setText(f"返回值类型错误: {type(info)}")
                    self.merge_video_info_label.setVisible(True)
                    return
                    
                if info.get('success', False):
                    info_text = f"时长: {info['duration_str']} | 分辨率: {info['size_str']} | 帧率: {info['fps']:.1f}fps"
                    self.merge_video_info_label.setText(info_text)
                    self.merge_video_info_label.setVisible(True)
                else:
                    error_msg = info.get('error', '未知错误')
                    self.merge_video_info_label.setText(f"获取视频信息失败: {error_msg}")
                    self.merge_video_info_label.setVisible(True)
            except Exception as e:
                import traceback
                error_detail = traceback.format_exc()
                self.merge_video_info_label.setText(f"获取视频信息出错: {str(e)}")
                self.merge_video_info_label.setVisible(True)
                print(f"视频信息获取错误详情: {error_detail}")
        else:
            self.merge_video_info_label.setText("视频处理功能不可用")
            self.merge_video_info_label.setVisible(True)
            
    def browse_audio_file_for_merge(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择音频文件", "", 
            "音频文件 (*.mp3 *.wav *.aac *.m4a *.flac)")
        if file_path:
            self.merge_audio_label.setText(os.path.basename(file_path))
            self.merge_audio_path = file_path
            # 启用播放音频按钮
            self.play_audio_btn.setEnabled(True)
            
    def browse_output_dir_for_split(self):
        dir_path = QFileDialog.getExistingDirectory(self, "选择输出目录")
        if dir_path:
            self.split_output_label.setText(dir_path)
            self.split_output_dir = dir_path
            
    def browse_output_file_for_extract(self):
        format_ext = self.audio_format_combo.currentText()
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存音频文件", f"extracted_audio.{format_ext}", 
            f"音频文件 (*.{format_ext})")
        if file_path:
            self.extract_output_label.setText(os.path.basename(file_path))
            self.extract_output_path = file_path
            
    def browse_output_file_for_merge(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存视频文件", "merged_video.mp4", 
            "视频文件 (*.mp4)")
        if file_path:
            self.merge_output_label.setText(os.path.basename(file_path))
            self.merge_output_path = file_path
    
    # 时间点管理方法
    def add_time_point(self):
        time_text = self.time_input.text().strip()
        if time_text:
            # 验证时间格式
            if self.validate_time_format(time_text):
                self.time_list.addItem(time_text)
                self.time_input.clear()
            else:
                QMessageBox.warning(self, "格式错误", "请输入正确的时间格式 (HH:MM:SS)")
                
    def remove_time_point(self):
        current_row = self.time_list.currentRow()
        if current_row >= 0:
            self.time_list.takeItem(current_row)
            
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
    
    # 处理方法
    def start_video_split(self):
        """开始视频拆分"""
        if not hasattr(self, 'split_file_path'):
            QMessageBox.warning(self, "错误", "请先选择视频文件")
            return
            
        if not hasattr(self, 'split_output_dir'):
            QMessageBox.warning(self, "错误", "请先选择输出目录")
            return
            
        if self.time_list.count() == 0:
            QMessageBox.warning(self, "错误", "请至少添加一个拆分时间点")
            return
            
        if not self.video_handler:
            QMessageBox.warning(self, "错误", "视频处理功能不可用")
            return
            
        # 获取时间点列表
        time_points = []
        for i in range(self.time_list.count()):
            time_points.append(self.time_list.item(i).text())
            
        # 启动工作线程
        self.split_progress.setVisible(True)
        self.split_progress.setRange(0, 100)
        self.split_progress.setValue(0)
        
        # 创建并启动视频拆分工作线程
        self.split_worker = VideoWorkerThread(
            "split",
            video_handler=self.video_handler,
            video_path=self.split_file_path,
            time_points=time_points,
            output_dir=self.split_output_dir
        )
        
        # 连接信号
        self.split_worker.progress_updated.connect(self.split_progress.setValue)
        self.split_worker.status_updated.connect(self.on_split_status)
        self.split_worker.finished_successfully.connect(self.on_split_finished)
        self.split_worker.error_occurred.connect(self.on_split_error)
        
        # 启动线程
        self.split_worker.start()
        
    def start_audio_extract(self):
        """开始音频提取"""
        if not hasattr(self, 'extract_file_path'):
            QMessageBox.warning(self, "错误", "请先选择视频文件")
            return
            
        if not hasattr(self, 'extract_output_path'):
            QMessageBox.warning(self, "错误", "请先选择输出文件")
            return
            
        if not self.video_handler:
            QMessageBox.warning(self, "错误", "视频处理功能不可用")
            return
            
        # 获取音频格式
        audio_format = self.audio_format_combo.currentText()
        
        # 启动工作线程
        self.extract_progress.setVisible(True)
        self.extract_progress.setRange(0, 100)
        self.extract_progress.setValue(0)
        
        # 创建并启动音频提取工作线程
        self.extract_worker = VideoWorkerThread(
            "extract",
            video_handler=self.video_handler,
            video_path=self.extract_file_path,
            output_path=self.extract_output_path,
            audio_format=audio_format
        )
        
        # 连接信号
        self.extract_worker.progress_updated.connect(self.extract_progress.setValue)
        self.extract_worker.status_updated.connect(self.on_extract_status)
        self.extract_worker.finished_successfully.connect(self.on_extract_finished)
        self.extract_worker.error_occurred.connect(self.on_extract_error)
        
        # 启动线程
        self.extract_worker.start()
        
    def start_video_merge(self):
        """开始视频合成"""
        if not hasattr(self, 'merge_video_path'):
            QMessageBox.warning(self, "错误", "请先选择视频文件")
            return
            
        if not hasattr(self, 'merge_audio_path'):
            QMessageBox.warning(self, "错误", "请先选择音频文件")
            return
            
        if not hasattr(self, 'merge_output_path'):
            QMessageBox.warning(self, "错误", "请先选择输出文件")
            return
            
        if not self.video_handler:
            QMessageBox.warning(self, "错误", "视频处理功能不可用")
            return
            
        # 获取合成选项
        replace_audio = self.replace_audio_checkbox.isChecked()
        
        # 启动工作线程
        self.merge_progress.setVisible(True)
        self.merge_progress.setRange(0, 100)
        self.merge_progress.setValue(0)
        
        # 创建并启动视频合成工作线程
        self.merge_worker = VideoWorkerThread(
            "merge",
            video_handler=self.video_handler,
            video_path=self.merge_video_path,
            audio_path=self.merge_audio_path,
            output_path=self.merge_output_path,
            replace_audio=replace_audio
        )
        
        # 连接信号
        self.merge_worker.progress_updated.connect(self.merge_progress.setValue)
        self.merge_worker.status_updated.connect(self.on_merge_status)
        self.merge_worker.finished_successfully.connect(self.on_merge_finished)
        self.merge_worker.error_occurred.connect(self.on_merge_error)
        
        # 启动线程
        self.merge_worker.start()
        
    # 视频拆分回调方法
    def on_split_status(self, message):
        """处理拆分状态更新"""
        print(f"拆分状态: {message}")
        
    def on_split_finished(self, result):
        """处理拆分完成"""
        self.split_progress.setVisible(False)
        if result.get('success', False):
            QMessageBox.information(self, "完成", f"视频拆分完成！\n输出目录: {self.split_output_dir}")
        else:
            error_msg = result.get('error', '未知错误')
            QMessageBox.critical(self, "错误", f"视频拆分失败: {error_msg}")
            
    def on_split_error(self, error_msg):
        """处理拆分错误"""
        self.split_progress.setVisible(False)
        QMessageBox.critical(self, "错误", f"视频拆分出错: {error_msg}")
        
    # 音频提取回调方法
    def on_extract_status(self, message):
        """处理提取状态更新"""
        print(f"提取状态: {message}")
        
    def on_extract_finished(self, result):
        """处理提取完成"""
        self.extract_progress.setVisible(False)
        if result.get('success', False):
            QMessageBox.information(self, "完成", f"音频提取完成！\n输出文件: {self.extract_output_path}")
        else:
            error_msg = result.get('error', '未知错误')
            QMessageBox.critical(self, "错误", f"音频提取失败: {error_msg}")
            
    def on_extract_error(self, error_msg):
        """处理提取错误"""
        self.extract_progress.setVisible(False)
        QMessageBox.critical(self, "错误", f"音频提取出错: {error_msg}")
        
    # 视频合成回调方法
    def on_merge_status(self, message):
        """处理合成状态更新"""
        print(f"合成状态: {message}")
        
    def on_merge_finished(self, result):
        """处理合成完成"""
        self.merge_progress.setVisible(False)
        if result.get('success', False):
            # 加载合成后的视频到播放器
            if hasattr(self, 'merge_output_path') and os.path.exists(self.merge_output_path):
                # 启用播放合成视频按钮
                self.play_merged_btn.setEnabled(True)
            QMessageBox.information(self, "完成", f"视频合成完成！\n输出文件: {self.merge_output_path}")
        else:
            error_msg = result.get('error', '未知错误')
            QMessageBox.critical(self, "错误", f"视频合成失败: {error_msg}")
            
    def on_merge_error(self, error_msg):
        """处理合成错误"""
        self.merge_progress.setVisible(False)
        QMessageBox.critical(self, "错误", f"视频合成出错: {error_msg}")
        
    def play_selected_video(self):
        """播放选中的视频文件"""
        if hasattr(self, 'merge_video_path'):
            self.merge_main_player.load_media(self.merge_video_path)
            # 自动开始播放
            self.merge_main_player.media_player.play()
            self.merge_main_player.play_button.setText("⏸")
            
    def play_selected_audio(self):
        """播放选中的音频文件"""
        if hasattr(self, 'merge_audio_path'):
            self.merge_main_player.load_media(self.merge_audio_path)
            # 自动开始播放
            self.merge_main_player.media_player.play()
            self.merge_main_player.play_button.setText("⏸")
            
    def play_merged_video(self):
        """播放合成后的视频文件"""
        if hasattr(self, 'merge_output_path') and os.path.exists(self.merge_output_path):
            self.merge_main_player.load_media(self.merge_output_path)
            # 自动开始播放
            self.merge_main_player.media_player.play()
            self.merge_main_player.play_button.setText("⏸")