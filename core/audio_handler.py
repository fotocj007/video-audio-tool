#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
音频处理核心模块 (兼容性包装器)
为了向后兼容，保留原有接口，内部委托给专门的模块
"""

import os
from typing import List, Dict, Tuple, Callable, Optional

# 导入拆分后的模块
from .audio_splitter import AudioSplitter
from .speech_to_text import SpeechToText

class AudioHandler:
    """音频处理类 (兼容性包装器)
    
    为了向后兼容，保留原有接口，内部委托给专门的模块:
    - AudioSplitter: 处理音频拆分
    - SpeechToText: 处理语音转文字
    """
    
    def __init__(self):
        """初始化音频处理器"""
        # 初始化专门的处理器
        self.audio_splitter = AudioSplitter()
        self.speech_to_text_handler = SpeechToText()
        
        # 为了向后兼容，保留这些属性
        self.ffmpeg_path = self.audio_splitter.ffmpeg_path
        self.ffprobe_path = self.audio_splitter.ffprobe_path
        self.whisper_model = None
        self.current_model_size = None
        
    def _setup_ffmpeg_path(self):
        """设置ffmpeg路径 (兼容性方法)"""
        # 委托给AudioSplitter
        self.audio_splitter._setup_ffmpeg_path()
        # 更新本地属性以保持兼容性
        self.ffmpeg_path = self.audio_splitter.ffmpeg_path
        self.ffprobe_path = self.audio_splitter.ffprobe_path
             
        self.whisper_model = None
        self.current_model_size = None
        
    def speech_to_text(self, audio_path: str, output_path: str, 
                      model_size: str = 'base', progress_callback: Optional[Callable] = None) -> Dict:
        """语音转文字 (兼容性方法)
        
        委托给SpeechToText模块处理
        """
        return self.speech_to_text_handler.speech_to_text(audio_path, output_path, model_size, progress_callback)
            
    def split_audio(self, audio_path: str, time_points: List[str],
                   output_dir: str, progress_callback: Optional[Callable] = None) -> Dict:
        """拆分音频文件 (兼容性方法)
        
        委托给AudioSplitter模块处理
        """
        return self.audio_splitter.split_audio(audio_path, time_points, output_dir, progress_callback)
    
    def _split_audio_with_ffmpeg(self, audio_path: str, time_points: List[str],
                                output_dir: str, progress_callback: Optional[Callable] = None) -> Dict:
        """使用FFmpeg拆分音频 (兼容性方法)"""
        return self.audio_splitter._split_audio_with_ffmpeg(audio_path, time_points, output_dir, progress_callback)
    
    def _split_audio_with_pydub(self, audio_path: str, time_points: List[str],
                               output_dir: str, progress_callback: Optional[Callable] = None) -> Dict:
        """使用pydub拆分音频 (兼容性方法)"""
        return self.audio_splitter._split_audio_with_pydub(audio_path, time_points, output_dir, progress_callback)
            
    def text_to_speech(self, text: str, output_path: str, use_clone: bool = False,
                      speaker: Optional[str] = None, clone_audio_path: Optional[str] = None,
                      progress_callback: Optional[Callable] = None) -> Dict:
        """文字转语音（已移除功能）"""
        return {
            'success': False,
            'error': 'TTS功能已移除'
        }
        
    def get_available_speakers(self) -> List[str]:
        """获取可用的说话人列表（已移除功能）"""
        return []
            
    def get_audio_info(self, audio_path: str) -> Dict:
        """获取音频文件信息 (兼容性方法)"""
        return self.audio_splitter.get_audio_info(audio_path)
    
    def _get_basic_audio_info(self, audio_path: str) -> Dict:
        """获取基本音频信息 (兼容性方法)"""
        return self.audio_splitter._get_basic_audio_info(audio_path)
            
    def _preprocess_audio(self, audio_path: str) -> str:
        """预处理音频文件 (兼容性方法)"""
        return self.speech_to_text_handler._preprocess_audio(audio_path)
            
    def _time_str_to_milliseconds(self, time_str: str) -> int:
        """将时间字符串转换为毫秒数 (兼容性方法)"""
        return self.audio_splitter._time_str_to_milliseconds(time_str)
    
    def _time_str_to_seconds(self, time_str: str) -> float:
        """将时间字符串转换为秒数 (兼容性方法)"""
        return self.audio_splitter._time_str_to_seconds(time_str)
            
    def _milliseconds_to_time_str(self, milliseconds: int) -> str:
        """将毫秒转换为时间字符串 (兼容性方法)"""
        return self.audio_splitter._milliseconds_to_time_str(milliseconds)