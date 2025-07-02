#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工作线程模块
用于处理耗时的多媒体处理任务，避免GUI界面冻结
"""

from PySide6.QtCore import QThread, Signal
import traceback

class VideoWorkerThread(QThread):
    """视频处理工作线程"""
    
    # 信号定义
    progress_updated = Signal(int)  # 进度更新
    status_updated = Signal(str)    # 状态更新
    finished_successfully = Signal(object)  # 成功完成
    error_occurred = Signal(str)    # 错误发生
    
    def __init__(self, task_type, **kwargs):
        super().__init__()
        self.task_type = task_type
        self.kwargs = kwargs
        self.is_cancelled = False
        
    def run(self):
        """线程主执行函数"""
        try:
            if self.task_type == "split":
                self._split_video()
            elif self.task_type == "extract":
                self._extract_audio()
            elif self.task_type == "merge":
                self._merge_video()
            else:
                self.error_occurred.emit(f"未知的任务类型: {self.task_type}")
                
        except Exception as e:
            error_msg = f"处理过程中发生错误: {str(e)}\n{traceback.format_exc()}"
            self.error_occurred.emit(error_msg)
            
    def _split_video(self):
        """视频拆分处理"""
        from core.video_handler import VideoHandler
        
        video_path = self.kwargs.get('video_path')
        time_points = self.kwargs.get('time_points')
        output_dir = self.kwargs.get('output_dir')
        
        self.status_updated.emit("正在加载视频文件...")
        
        handler = VideoHandler()
        result = handler.split_video(video_path, time_points, output_dir, 
                                   progress_callback=self._update_progress)
        
        if result['success']:
            self.finished_successfully.emit(result)
        else:
            self.error_occurred.emit(result['error'])
            
    def _extract_audio(self):
        """音频提取处理"""
        from core.video_handler import VideoHandler
        
        video_path = self.kwargs.get('video_path')
        output_path = self.kwargs.get('output_path')
        audio_format = self.kwargs.get('audio_format', 'mp3')
        
        self.status_updated.emit("正在提取音频...")
        
        handler = VideoHandler()
        result = handler.extract_audio(video_path, output_path, audio_format,
                                     progress_callback=self._update_progress)
        
        if result['success']:
            self.finished_successfully.emit(result)
        else:
            self.error_occurred.emit(result['error'])
            
    def _merge_video(self):
        """视频合成处理"""
        from core.video_handler import VideoHandler
        
        video_path = self.kwargs.get('video_path')
        audio_path = self.kwargs.get('audio_path')
        output_path = self.kwargs.get('output_path')
        replace_audio = self.kwargs.get('replace_audio', True)
        
        self.status_updated.emit("正在合成视频...")
        
        handler = VideoHandler()
        result = handler.merge_video_audio(video_path, audio_path, output_path, 
                                         replace_audio, progress_callback=self._update_progress)
        
        if result['success']:
            self.finished_successfully.emit(result)
        else:
            self.error_occurred.emit(result['error'])
            
    def _update_progress(self, progress):
        """更新进度"""
        if not self.is_cancelled:
            self.progress_updated.emit(int(progress))
            
    def cancel(self):
        """取消任务"""
        self.is_cancelled = True
        self.quit()
        
class AudioWorkerThread(QThread):
    """音频处理工作线程"""
    
    # 信号定义
    progress_updated = Signal(int)  # 进度更新
    status_updated = Signal(str)    # 状态更新
    finished_successfully = Signal(str)  # 成功完成
    error_occurred = Signal(str)    # 错误发生
    transcription_result = Signal(str)  # 转录结果
    
    def __init__(self, task_type, **kwargs):
        super().__init__()
        self.task_type = task_type
        self.kwargs = kwargs
        self.is_cancelled = False
        
    def run(self):
        """线程主执行函数"""
        try:
            if self.task_type == "stt":
                self._speech_to_text()
            elif self.task_type == "split":
                self._split_audio()
            elif self.task_type == "tts" or self.task_type == "tts_test":
                self._text_to_speech()
            else:
                self.error_occurred.emit(f"未知的任务类型: {self.task_type}")
                
        except Exception as e:
            error_msg = f"处理过程中发生错误: {str(e)}\n{traceback.format_exc()}"
            self.error_occurred.emit(error_msg)
            
    def _speech_to_text(self):
        """语音转文字处理"""
        from core.audio_handler import AudioHandler
        
        audio_path = self.kwargs.get('audio_path')
        output_path = self.kwargs.get('output_path')
        model_size = self.kwargs.get('model_size', 'base')
        
        self.status_updated.emit("正在加载Whisper模型...")
        
        handler = AudioHandler()
        result = handler.speech_to_text(audio_path, output_path, model_size,
                                      progress_callback=self._update_progress)
        
        if result['success']:
            self.transcription_result.emit(result['text'])
            self.finished_successfully.emit("语音转文字完成！")
        else:
            self.error_occurred.emit(result['error'])
            
    def _split_audio(self):
        """音频拆分处理"""
        from core.audio_handler import AudioHandler
        
        audio_path = self.kwargs.get('audio_path')
        time_points = self.kwargs.get('time_points')
        output_dir = self.kwargs.get('output_dir')
        
        self.status_updated.emit("正在加载音频文件...")
        
        handler = AudioHandler()
        result = handler.split_audio(audio_path, time_points, output_dir,
                                   progress_callback=self._update_progress)
        
        if result['success']:
            self.finished_successfully.emit(f"音频拆分完成！生成了 {len(result['output_files'])} 个文件")
        else:
            self.error_occurred.emit(result['error'])
            
    def _text_to_speech(self):
        """文字转语音处理"""
        try:
            from TTS.api import TTS
        except ImportError:
            self.error_occurred.emit("TTS库未安装或不可用")
            return
        
        text = self.kwargs.get('text')
        output_path = self.kwargs.get('output_path')
        model_name = self.kwargs.get('model_name', 'tts_models/zh-CN/baker/tacotron2-DDC-GST')
        language = self.kwargs.get('language', 'auto')
        use_clone = self.kwargs.get('use_clone', False)
        clone_audio_path = self.kwargs.get('clone_audio_path')
        
        self.status_updated.emit("正在加载TTS模型...")
        
        try:
            # 预处理文本，避免多余语音
            processed_text = self._preprocess_text(text)
            
            # 初始化TTS模型
            tts = TTS(model_name=model_name)
            
            self.status_updated.emit("正在生成语音...")
            
            # 检查模型是否支持多语言
            is_multilingual = self._is_multilingual_model(model_name)
            
            # 自动检测语言（仅在多语言模型时使用）
            detected_language = None
            if is_multilingual and language == 'auto':
                detected_language = self._detect_language(processed_text)
            elif is_multilingual and language != 'auto':
                detected_language = language
            
            # 生成语音
            if use_clone and clone_audio_path:
                if is_multilingual and detected_language:
                    tts.tts_to_file(text=processed_text, file_path=output_path, speaker_wav=clone_audio_path, language=detected_language)
                else:
                    tts.tts_to_file(text=processed_text, file_path=output_path, speaker_wav=clone_audio_path)
            else:
                if is_multilingual and detected_language:
                    tts.tts_to_file(text=processed_text, file_path=output_path, language=detected_language)
                else:
                    tts.tts_to_file(text=processed_text, file_path=output_path)
            
            self.finished_successfully.emit("文字转语音完成！")
            
        except Exception as e:
            self.error_occurred.emit(f"TTS处理失败: {str(e)}")
            
    def _preprocess_text(self, text):
        """预处理文本，清理和规范化"""
        import re
        
        if not text or not text.strip():
            return text
        
        # 移除多余的空白字符
        text = re.sub(r'\s+', ' ', text.strip())
        
        # 规范化标点符号
        text = text.replace('。。', '。')
        text = text.replace('，，', '，')
        text = text.replace('！！', '！')
        text = text.replace('？？', '？')
        
        # 移除多余的换行符
        text = text.replace('\n', ' ').replace('\r', ' ')
        
        # 确保句子结尾有适当的标点
        if text and not text[-1] in '。！？.!?':
            # 根据语言添加适当的句号
            if any('\u4e00' <= char <= '\u9fff' for char in text):
                text += '。'  # 中文句号
            else:
                text += '.'   # 英文句号
        
        return text
    
    def _detect_language(self, text):
        """简单的语言检测"""
        import re
        
        # 检测中文字符
        chinese_pattern = re.compile(r'[\u4e00-\u9fff]')
        # 检测日文字符
        japanese_pattern = re.compile(r'[\u3040-\u309f\u30a0-\u30ff]')
        # 检测韩文字符
        korean_pattern = re.compile(r'[\uac00-\ud7af]')
        
        if chinese_pattern.search(text):
            return 'zh'
        elif japanese_pattern.search(text):
            return 'ja'
        elif korean_pattern.search(text):
            return 'ko'
        else:
            # 默认为英文
            return 'en'
    
    def _is_multilingual_model(self, model_name):
        """检查模型是否支持多语言"""
        # 多语言模型通常包含这些关键词
        multilingual_keywords = [
            'multilingual',
            'multi-dataset', 
            'xtts',
            'bark',
            'multi_speaker'
        ]
        
        model_name_lower = model_name.lower()
        return any(keyword in model_name_lower for keyword in multilingual_keywords)
            
    def _update_progress(self, progress):
        """更新进度"""
        if not self.is_cancelled:
            self.progress_updated.emit(int(progress))
            
    def cancel(self):
        """取消任务"""
        self.is_cancelled = True
        self.quit()