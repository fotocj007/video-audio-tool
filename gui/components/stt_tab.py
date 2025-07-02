#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
语音转文字标签页组件
实现语音转文字功能的用户界面
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QComboBox, QTextEdit, QProgressBar, QFileDialog,
    QMessageBox, QGroupBox, QGridLayout
)
from PySide6.QtCore import Qt
import os
from core.audio_handler import AudioHandler
from .audio_player import AudioPlayerWidget


class STTTabWidget(QWidget):
    """语音转文字标签页"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.audio_handler = AudioHandler()
        self.stt_file_path = None
        self.stt_output_path = None
        self.stt_worker = None
        
        self.init_ui()
        
    def init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout(self)
        
        # 文件选择组
        file_group = QGroupBox("选择音频文件")
        file_layout = QHBoxLayout(file_group)
        
        self.stt_file_label = QLabel("未选择文件")
        self.stt_file_label.setStyleSheet("QLabel { padding: 5px; border: 1px solid #ccc; }")
        file_layout.addWidget(self.stt_file_label)
        
        stt_browse_btn = QPushButton("浏览")
        stt_browse_btn.clicked.connect(self.browse_audio_file)
        file_layout.addWidget(stt_browse_btn)
        
        layout.addWidget(file_group)
        
        # 音频信息显示
        self.audio_info_label = QLabel("音频信息: 未选择文件")
        self.audio_info_label.setStyleSheet("QLabel { color: #666; font-size: 12px; padding: 5px; }")
        layout.addWidget(self.audio_info_label)
        
        # 音频播放控件
        self.audio_player = AudioPlayerWidget("stt", self)
        player_group = QGroupBox("音频播放控制")
        player_layout = QVBoxLayout(player_group)
        player_layout.addWidget(self.audio_player)
        layout.addWidget(player_group)
        
        # 模型设置组
        model_group = QGroupBox("模型设置")
        model_layout = QGridLayout(model_group)
        
        model_layout.addWidget(QLabel("Whisper模型:"), 0, 0)
        self.whisper_model_combo = QComboBox()
        self.whisper_model_combo.addItems(["tiny", "base", "small", "medium", "large"])
        self.whisper_model_combo.setCurrentText("base")
        model_layout.addWidget(self.whisper_model_combo, 0, 1)
        
        model_info_label = QLabel("模型说明：tiny(最快), base(平衡), small(较好), medium(更好), large(最佳)")
        model_info_label.setStyleSheet("QLabel { color: #666; font-size: 12px; }")
        model_layout.addWidget(model_info_label, 1, 0, 1, 2)
        
        layout.addWidget(model_group)
        
        # 输出设置组
        output_group = QGroupBox("输出设置")
        output_layout = QHBoxLayout(output_group)
        
        output_layout.addWidget(QLabel("输出文件:"))
        self.output_label = QLabel("未选择文件")
        self.output_label.setStyleSheet("QLabel { padding: 5px; border: 1px solid #ccc; }")
        output_layout.addWidget(self.output_label)
        
        output_btn = QPushButton("选择保存位置")
        output_btn.clicked.connect(self.browse_output_file)
        output_layout.addWidget(output_btn)
        
        layout.addWidget(output_group)
        
        # 结果预览
        preview_group = QGroupBox("转录结果预览")
        preview_layout = QVBoxLayout(preview_group)
        
        self.result_text = QTextEdit()
        self.result_text.setMaximumHeight(150)
        self.result_text.setPlaceholderText("转录结果将在这里显示...")
        preview_layout.addWidget(self.result_text)
        
        layout.addWidget(preview_group)
        
        # 进度条和开始按钮
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)
        
        start_btn = QPushButton("开始转录")
        start_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border: none;
                padding: 10px;
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        start_btn.clicked.connect(self.start_transcription)
        layout.addWidget(start_btn)
        
        layout.addStretch()
        
    def browse_audio_file(self):
        """浏览音频文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择音频文件", "", 
            "音频文件 (*.mp3 *.wav *.m4a *.flac *.aac *.ogg)")
        if file_path:
            self.stt_file_label.setText(os.path.basename(file_path))
            self.stt_file_path = file_path
            self.update_audio_info(file_path)
            
    def browse_output_file(self):
        """浏览输出文件"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存文本文件", "transcription.txt", 
            "文本文件 (*.txt)")
        if file_path:
            self.output_label.setText(os.path.basename(file_path))
            self.stt_output_path = file_path
            
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
            
    def start_transcription(self):
        """开始语音转文字"""
        if not self.stt_file_path:
            QMessageBox.warning(self, "错误", "请先选择音频文件")
            return
            
        if not self.stt_output_path:
            QMessageBox.warning(self, "错误", "请先选择输出文件")
            return
            
        # 获取选择的模型大小
        model_size = self.whisper_model_combo.currentText()
        
        # 启动工作线程
        self.progress.setVisible(True)
        self.progress.setRange(0, 100)
        
        from gui.worker_threads import AudioWorkerThread
        
        self.stt_worker = AudioWorkerThread(
            'stt',
            audio_path=self.stt_file_path,
            output_path=self.stt_output_path,
            model_size=model_size
        )
        
        # 连接信号
        self.stt_worker.progress_updated.connect(self.progress.setValue)
        self.stt_worker.status_updated.connect(lambda msg: print(f"状态: {msg}"))
        self.stt_worker.transcription_result.connect(self.on_transcription_result)
        self.stt_worker.finished_successfully.connect(self.on_finished)
        self.stt_worker.error_occurred.connect(self.on_error)
        
        # 启动线程
        self.stt_worker.start()
        
        print(f'开始语音转文字处理: {self.stt_file_path} -> {self.stt_output_path}')
        
    def on_transcription_result(self, text):
        """处理转录结果"""
        self.result_text.setPlainText(text)
        
    def on_finished(self, message):
        """转录完成处理"""
        self.progress.setVisible(False)
        QMessageBox.information(self, "完成", message)
        print(f"语音转文字完成: {message}")
        
    def on_error(self, error_message):
        """转录错误处理"""
        self.progress.setVisible(False)
        QMessageBox.critical(self, "错误", f"语音转文字失败:\n{error_message}")
        print(f"语音转文字错误: {error_message}")