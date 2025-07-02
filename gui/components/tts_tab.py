#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文字转语音标签页组件
实现文字转语音功能的用户界面
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QComboBox, QTextEdit, QProgressBar, QFileDialog,
    QMessageBox, QGroupBox, QGridLayout, QCheckBox
)
from PySide6.QtCore import Qt, QProcess
import os
import tempfile

try:
    from TTS.api import TTS
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False


class TTSTabWidget(QWidget):
    """文字转语音标签页"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tts_voice_file = None
        self.tts_output_file = None
        self.tts_worker = None
        self.tts_test_worker = None
        self.temp_audio_process = None
        self.user_audio_process = None
        
        self.init_ui()
        
    def init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout(self)
        
        if not TTS_AVAILABLE:
            # TTS不可用时显示提示信息
            error_label = QLabel("TTS库未安装或不可用，请安装TTS库后重启应用")
            error_label.setStyleSheet("QLabel { color: red; font-size: 14px; padding: 20px; }")
            error_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(error_label)
            return
        
        # 文本输入组
        text_group = QGroupBox("输入文本")
        text_layout = QVBoxLayout(text_group)
        
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("请输入要转换为语音的文本...")
        self.text_input.setMaximumHeight(150)
        text_layout.addWidget(self.text_input)
        
        layout.addWidget(text_group)
        
        # 语音设置组
        voice_group = QGroupBox("语音设置")
        voice_layout = QGridLayout(voice_group)
        
        # TTS模型选择
        voice_layout.addWidget(QLabel("TTS模型:"), 0, 0)
        self.model_combo = QComboBox()
        # 添加常用的TTS模型
        self.model_combo.addItems([
            "tts_models/zh-CN/baker/tacotron2-DDC-GST",
            "tts_models/en/ljspeech/tacotron2-DDC",
            "tts_models/en/ljspeech/glow-tts",
            "tts_models/multilingual/multi-dataset/your_tts"
        ])
        voice_layout.addWidget(self.model_combo, 0, 1)
        
        # 语言选择
        voice_layout.addWidget(QLabel("语言:"), 1, 0)
        self.language_combo = QComboBox()
        self.language_combo.addItems([
            "zh",  # 中文
            "en",  # 英文
            "ja",  # 日文
            "ko",  # 韩文
            "es",  # 西班牙文
            "fr",  # 法文
            "de",  # 德文
            "auto"  # 自动检测
        ])
        voice_layout.addWidget(self.language_combo, 1, 1)
        
        # 语音克隆选项
        voice_layout.addWidget(QLabel("语音克隆:"), 2, 0)
        self.voice_clone_checkbox = QCheckBox("使用自定义语音")
        self.voice_clone_checkbox.toggled.connect(self.toggle_voice_clone)
        voice_layout.addWidget(self.voice_clone_checkbox, 2, 1)
        
        # 自定义语音文件选择
        self.voice_file_layout = QHBoxLayout()
        self.voice_file_label = QLabel("未选择语音文件")
        self.voice_file_label.setStyleSheet("QLabel { padding: 5px; border: 1px solid #ccc; }")
        self.voice_file_layout.addWidget(self.voice_file_label)
        
        self.voice_browse_btn = QPushButton("浏览")
        self.voice_browse_btn.clicked.connect(self.browse_voice_file)
        self.voice_file_layout.addWidget(self.voice_browse_btn)
        
        voice_layout.addLayout(self.voice_file_layout, 3, 0, 1, 2)
        
        # 初始状态下隐藏语音文件选择
        self.voice_file_label.setVisible(False)
        self.voice_browse_btn.setVisible(False)
        
        layout.addWidget(voice_group)
        
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
        
        # 预览和控制按钮
        button_layout = QHBoxLayout()
        
        test_voice_btn = QPushButton("试听语音")
        test_voice_btn.clicked.connect(self.test_voice)
        button_layout.addWidget(test_voice_btn)
        
        generate_btn = QPushButton("生成音频")
        generate_btn.setStyleSheet("""
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
        generate_btn.clicked.connect(self.start_generation)
        button_layout.addWidget(generate_btn)
        
        layout.addLayout(button_layout)
        
        # 进度条
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)
        
        layout.addStretch()
        
    def toggle_voice_clone(self, checked):
        """切换语音克隆选项"""
        self.voice_file_label.setVisible(checked)
        self.voice_browse_btn.setVisible(checked)
    
    def browse_voice_file(self):
        """浏览语音文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择语音文件",
            "",
            "音频文件 (*.wav *.mp3 *.flac *.m4a);;所有文件 (*)"
        )
        if file_path:
            self.voice_file_label.setText(os.path.basename(file_path))
            self.tts_voice_file = file_path
    
    def browse_output_file(self):
        """浏览TTS输出文件"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "选择输出文件",
            "",
            "音频文件 (*.wav);;所有文件 (*)"
        )
        if file_path:
            if not file_path.endswith('.wav'):
                file_path += '.wav'
            self.output_label.setText(os.path.basename(file_path))
            self.tts_output_file = file_path
    
    def test_voice(self):
        """试听TTS语音或用户上传的音频"""
        # 如果选择了语音克隆且已上传音频文件，直接播放用户音频
        if self.voice_clone_checkbox.isChecked() and hasattr(self, 'tts_voice_file'):
            self.play_user_audio(self.tts_voice_file)
            return
        
        if not TTS_AVAILABLE:
            QMessageBox.warning(self, "错误", "TTS库不可用")
            return
        
        text = self.text_input.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "错误", "请输入要转换的文本")
            return
        
        # 创建临时文件用于试听
        temp_file = tempfile.mktemp(suffix='.wav')
        
        # 显示进度条
        self.progress.setVisible(True)
        self.progress.setRange(0, 0)  # 不确定进度
        
        # 创建TTS工作线程
        from gui.worker_threads import AudioWorkerThread
        
        self.tts_test_worker = AudioWorkerThread(
            "tts_test",
            text=text,
            output_path=temp_file,
            model_name=self.model_combo.currentText(),
            language=self.language_combo.currentText(),
            use_clone=self.voice_clone_checkbox.isChecked(),
            clone_audio_path=getattr(self, 'tts_voice_file', None)
        )
        
        # 连接信号
        self.tts_test_worker.finished_successfully.connect(lambda: self.on_test_finished(temp_file))
        self.tts_test_worker.error_occurred.connect(self.on_test_error)
        
        # 启动线程
        self.tts_test_worker.start()
    
    def start_generation(self):
        """开始TTS生成"""
        if not TTS_AVAILABLE:
            QMessageBox.warning(self, "错误", "TTS库不可用")
            return
        
        text = self.text_input.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "错误", "请输入要转换的文本")
            return
        
        if not hasattr(self, 'tts_output_file'):
            QMessageBox.warning(self, "错误", "请选择输出文件")
            return
        
        # 检查语音克隆设置
        if self.voice_clone_checkbox.isChecked() and not hasattr(self, 'tts_voice_file'):
            QMessageBox.warning(self, "错误", "选择语音克隆时必须上传参考音频文件")
            return
        
        # 显示进度条
        self.progress.setVisible(True)
        self.progress.setRange(0, 0)  # 不确定进度
        
        # 创建TTS工作线程
        from gui.worker_threads import AudioWorkerThread
        
        self.tts_worker = AudioWorkerThread(
            "tts",
            text=text,
            output_path=self.tts_output_file,
            model_name=self.model_combo.currentText(),
            language=self.language_combo.currentText(),
            use_clone=self.voice_clone_checkbox.isChecked(),
            clone_audio_path=getattr(self, 'tts_voice_file', None)
        )
        
        # 连接信号
        self.tts_worker.finished_successfully.connect(self.on_generation_finished)
        self.tts_worker.error_occurred.connect(self.on_generation_error)
        
        # 启动线程
        self.tts_worker.start()
    
    def on_test_finished(self, temp_file):
        """TTS试听完成回调"""
        self.progress.setVisible(False)
        # 播放试听
        self.play_temp_audio(temp_file)
    
    def on_test_error(self, error_message):
        """TTS试听错误回调"""
        self.progress.setVisible(False)
        QMessageBox.critical(self, "错误", f"生成试听语音时发生错误: {error_message}")
    
    def on_generation_finished(self, message):
        """TTS生成完成回调"""
        self.progress.setVisible(False)
        QMessageBox.information(self, "完成", f"音频已生成: {self.tts_output_file}")
    
    def on_generation_error(self, error_message):
        """TTS生成错误回调"""
        self.progress.setVisible(False)
        QMessageBox.critical(self, "错误", f"生成音频时发生错误: {error_message}")
    
    def play_temp_audio(self, file_path):
        """播放临时音频文件"""
        try:
            # 获取ffplay.exe路径
            ffplay_path = os.path.join(os.getcwd(), "ffplay.exe")
            if not os.path.exists(ffplay_path):
                QMessageBox.warning(self, "错误", "找不到ffplay.exe文件")
                return
            
            # 停止之前的播放进程（如果存在）
            if hasattr(self, 'temp_audio_process') and self.temp_audio_process is not None and self.temp_audio_process.state() != QProcess.NotRunning:
                self.temp_audio_process.kill()
            
            # 创建播放进程
            self.temp_audio_process = QProcess(self)
            args = [
                "-nodisp",  # 不显示视频窗口
                "-autoexit",  # 播放完成后自动退出
                file_path
            ]
            
            # 连接信号，播放完成后清理临时文件
            self.temp_audio_process.finished.connect(lambda: self.on_temp_audio_finished(file_path))
            
            # 非阻塞启动
            self.temp_audio_process.start(ffplay_path, args)
                
        except Exception as e:
            QMessageBox.critical(self, "播放错误", f"播放音频时发生错误: {str(e)}")
    
    def on_temp_audio_finished(self, file_path):
        """临时音频播放完成回调"""
        try:
            # 清理临时文件
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"清理临时文件失败: {str(e)}")
    
    def play_user_audio(self, file_path):
        """播放用户上传的音频文件"""
        try:
            # 获取ffplay.exe路径
            ffplay_path = os.path.join(os.getcwd(), "ffplay.exe")
            if not os.path.exists(ffplay_path):
                QMessageBox.warning(self, "错误", "找不到ffplay.exe文件")
                return
            
            # 停止之前的播放进程（如果存在）
            if hasattr(self, 'user_audio_process') and self.user_audio_process is not None and self.user_audio_process.state() != QProcess.NotRunning:
                self.user_audio_process.kill()
            
            # 创建播放进程
            self.user_audio_process = QProcess(self)
            args = [
                "-nodisp",  # 不显示视频窗口
                "-autoexit",  # 播放完成后自动退出
                file_path
            ]
            
            # 连接信号（可选，用于处理播放完成事件）
            self.user_audio_process.finished.connect(self.on_user_audio_finished)
            
            # 非阻塞启动
            self.user_audio_process.start(ffplay_path, args)
                
        except Exception as e:
            QMessageBox.critical(self, "播放错误", f"播放音频时发生错误: {str(e)}")
    
    def on_user_audio_finished(self):
        """用户音频播放完成回调"""
        # 可以在这里添加播放完成后的处理逻辑
        pass