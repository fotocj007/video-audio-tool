#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
音频处理模块GUI（重构版本）
使用组件化设计，实现语音转文字、音频拆分、文字转语音等功能的用户界面
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTabWidget
)
from PySide6.QtCore import Qt

from .components.stt_tab import STTTabWidget
from .components.split_tab import SplitTabWidget
from .components.tts_tab import TTSTabWidget


class AudioProcessorWidget(QWidget):
    """音频处理主窗口部件（重构版本）"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout(self)
        
        # 创建标签页
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)
        
        # 语音转文字标签页
        self.stt_tab = STTTabWidget()
        tab_widget.addTab(self.stt_tab, "语音转文字")
        
        # 音频拆分标签页
        self.split_tab = SplitTabWidget()
        tab_widget.addTab(self.split_tab, "音频拆分")
        
        # 文字转音频标签页
        self.tts_tab = TTSTabWidget()
        tab_widget.addTab(self.tts_tab, "文字转音频")