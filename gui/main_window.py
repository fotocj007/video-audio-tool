#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主窗口类
实现应用程序的主界面，包含菜单栏和功能切换
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QStackedWidget, QMenuBar, QStatusBar, QLabel,
    QMessageBox
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QIcon, QAction

from gui.video_processor import VideoProcessorWidget
from gui.audio_processor import AudioProcessorWidget
from simple_config import get_config, is_feature_enabled, get_window_geometry, set_window_geometry
from core import VIDEO_HANDLER_AVAILABLE, AUDIO_HANDLER_AVAILABLE

class MainWindow(QMainWindow):
    """主窗口类"""
    
    def __init__(self):
        super().__init__()
        print("  - 开始初始化UI...")
        self.init_ui()
        print("  - UI初始化完成，设置菜单...")
        self.setup_menu()
        print("  - 菜单设置完成，设置状态栏...")
        self.setup_status_bar()
        print("  - 状态栏设置完成，检查功能...")
        self.check_features()
        print("  - 功能检查完成，主窗口初始化完成")
        
    def init_ui(self):
        """初始化用户界面"""
        # 从配置获取窗口信息
        app_name = get_config('app.name', '多媒体处理工具')
        app_version = get_config('app.version', '1.0.0')
        self.setWindowTitle(f"{app_name} v{app_version}")
        
        # 设置窗口几何
        geometry = get_window_geometry()
        self.setMinimumSize(QSize(1000, 700))
        self.resize(geometry['width'], geometry['height'])
        self.move(geometry['x'], geometry['y'])
        
        # 创建中央窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # 创建标题标签
        title_label = QLabel("多媒体处理工具")
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                padding: 20px;
                background-color: #ecf0f1;
                border-radius: 10px;
                margin-bottom: 10px;
            }
        """)
        main_layout.addWidget(title_label)
        
        # 创建堆叠窗口部件
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)
        
        # 创建功能页面（根据可用性）
        self.page_indices = {}
        current_index = 0
        
        # 创建视频处理页面
        if is_feature_enabled('video_processing') and VIDEO_HANDLER_AVAILABLE:
            print("    - 创建视频处理页面...")
            self.video_processor = VideoProcessorWidget()
            self.stacked_widget.addWidget(self.video_processor)
            self.page_indices['video'] = current_index
            current_index += 1
            print("    - 视频处理页面创建完成")
        else:
            print("    - 跳过视频处理页面（功能未启用或依赖不可用）")
            self.video_processor = None
        
        # 创建音频处理页面
        if is_feature_enabled('audio_processing') and AUDIO_HANDLER_AVAILABLE:
            print("    - 创建音频处理页面...")
            self.audio_processor = AudioProcessorWidget()
            self.stacked_widget.addWidget(self.audio_processor)
            self.page_indices['audio'] = current_index
            current_index += 1
            print("    - 音频处理页面创建完成")
        else:
            print("    - 跳过音频处理页面（功能未启用或依赖不可用）")
            self.audio_processor = None
        
        # 默认显示第一个可用页面
        if self.page_indices:
            self.stacked_widget.setCurrentIndex(0)
        
    def setup_menu(self):
        """设置菜单栏"""
        menubar = self.menuBar()
        
        # 功能菜单
        function_menu = menubar.addMenu("功能")
        
        # 视频处理菜单项
        if 'video' in self.page_indices:
            video_action = QAction("视频处理", self)
            video_action.setStatusTip("切换到视频处理功能")
            video_action.triggered.connect(lambda: self.switch_to_page('video'))
            function_menu.addAction(video_action)
        
        # 音频处理菜单项
        if 'audio' in self.page_indices:
            audio_action = QAction("音频处理", self)
            audio_action.setStatusTip("切换到音频处理功能")
            audio_action.triggered.connect(lambda: self.switch_to_page('audio'))
            function_menu.addAction(audio_action)
        
        function_menu.addSeparator()
        
        # 退出菜单项
        exit_action = QAction("退出", self)
        exit_action.setStatusTip("退出应用程序")
        exit_action.triggered.connect(self.close)
        function_menu.addAction(exit_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu("帮助")
        
        # 关于菜单项
        about_action = QAction("关于", self)
        about_action.setStatusTip("关于本软件")
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def setup_status_bar(self):
        """设置状态栏"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪")
        
    def switch_to_page(self, page_name):
        """切换到指定页面"""
        if page_name in self.page_indices:
            index = self.page_indices[page_name]
            self.stacked_widget.setCurrentIndex(index)
            if page_name == 'video':
                self.status_bar.showMessage("当前功能：视频处理")
            elif page_name == 'audio':
                self.status_bar.showMessage("当前功能：音频处理")
            
    def show_about(self):
        """显示关于对话框"""
        QMessageBox.about(self, "关于", 
                         "多媒体处理工具 v1.0\n\n"
                         "一款基于Python的视频和音频处理桌面应用程序\n\n"
                         "主要功能：\n"
                         "• 视频拆分、提取音频、合成视频\n"
                         "• 语音转文字、音频拆分、文字转语音\n\n"
                         "技术栈：PySide6, MoviePy, Whisper, TTS")
        
    def update_status(self, message):
        """更新状态栏消息"""
        self.status_bar.showMessage(message)
    
    def check_features(self):
        """检查功能可用性并显示警告"""
        warnings = []
        
        if not VIDEO_HANDLER_AVAILABLE:
            warnings.append("视频处理功能不可用：缺少 moviepy 依赖")
        
        if not AUDIO_HANDLER_AVAILABLE:
            warnings.append("音频处理功能不可用：缺少相关依赖")
        
        if warnings:
            warning_msg = "\n".join(warnings)
            warning_msg += "\n\n请运行 install_dependencies.py 安装依赖包"
            QMessageBox.warning(self, "功能警告", warning_msg)
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        # 保存窗口几何信息
        geometry = self.geometry()
        set_window_geometry(
            geometry.width(), 
            geometry.height(), 
            geometry.x(), 
            geometry.y()
        )
        event.accept()