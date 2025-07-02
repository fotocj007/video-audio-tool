#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视频处理核心模块（重构版）
使用模块化结构，保持向后兼容性
"""

import os
import sys
from typing import List, Dict, Callable, Optional
import traceback

# 导入新的模块化组件
from .unified_video_handler import UnifiedVideoHandler
from .base_handler import BaseVideoHandler

class VideoHandler:
    """视频处理类（向后兼容包装器）"""
    
    def __init__(self):
        """初始化视频处理器"""
        self.current_clip = None
        
        # 使用新的统一处理器
        try:
            self._handler = UnifiedVideoHandler()
            print("VideoHandler初始化成功，使用模块化架构")
        except Exception as e:
            print(f"VideoHandler初始化失败: {e}")
            # 创建基础处理器作为备选
            self._handler = BaseVideoHandler()
            print("使用基础处理器作为备选方案")
        
    # ==================== 向后兼容的方法委托 ====================
    
    def split_video(self, video_path: str, time_points: List[str], 
                   output_dir: str, progress_callback: Optional[Callable] = None) -> Dict:
        """拆分视频文件（委托给新模块）"""
        return self._handler.split_video(video_path, time_points, output_dir, progress_callback)
    
    def extract_audio(self, video_path: str, output_path: str, audio_format: str = 'mp3', progress_callback: Optional[Callable] = None) -> Dict:
        """提取音频 - 委托给AudioExtractor"""
        return self._handler.extract_audio(video_path, output_path, audio_format, progress_callback)
    
    def merge_video_audio(self, video_path: str, audio_path: str, output_path: str,
                         replace_audio: bool = True, progress_callback: Optional[Callable] = None) -> Dict:
        """合并视频音频（委托给新模块）"""
        return self._handler.merge_video_audio(video_path, audio_path, output_path, replace_audio, progress_callback)
    
    # ==================== 保留的原有方法 ====================
    
    def test_ffmpeg_config(self) -> bool:
        """测试FFmpeg配置（委托给基础处理器）"""
        return self._handler.test_ffmpeg_config()
    
    def get_video_info(self, video_path: str) -> dict:
        """获取视频信息（委托给基础处理器）"""
        return self._handler.get_video_info(video_path)
    
    def _time_str_to_seconds(self, time_str: str) -> float:
        """时间字符串转秒数（委托给基础处理器）"""
        return self._handler._time_str_to_seconds(time_str)
    
    def _seconds_to_time_str(self, seconds: float) -> str:
        """秒数转时间字符串（委托给基础处理器）"""
        return self._handler._seconds_to_time_str(seconds)
    
    # ==================== 新增的便捷方法 ====================
    
    def extract_audio_segment(self, video_path: str, output_path: str,
                            start_time: float, end_time: float,
                            progress_callback: Optional[Callable] = None) -> Dict:
        """提取音频片段"""
        return self._handler.extract_audio_segment(video_path, output_path, start_time, end_time, progress_callback)
    
    def replace_audio(self, video_path: str, audio_path: str, output_path: str,
                     progress_callback: Optional[Callable] = None) -> Dict:
        """替换音频轨道"""
        return self._handler.replace_audio(video_path, audio_path, output_path, progress_callback)
    
    def remove_audio(self, video_path: str, output_path: str,
                    progress_callback: Optional[Callable] = None) -> Dict:
        """移除音频轨道"""
        return self._handler.remove_audio(video_path, output_path, progress_callback)
    
    def get_audio_info(self, video_path: str) -> Dict:
        """获取音频信息"""
        return self._handler.get_audio_info(video_path)
    
    def batch_split_videos(self, video_configs: List[Dict], 
                          progress_callback: Optional[Callable] = None) -> Dict:
        """批量拆分视频"""
        return self._handler.batch_split_videos(video_configs, progress_callback)
    
    def batch_extract_audio(self, video_audio_configs: List[Dict],
                           progress_callback: Optional[Callable] = None) -> Dict:
        """批量提取音频"""
        return self._handler.batch_extract_audio(video_audio_configs, progress_callback)
    
    def get_supported_formats(self) -> Dict:
        """获取支持的格式"""
        return self._handler.get_supported_formats()
    
    def validate_time_points(self, time_points: List[str], video_duration: float) -> Dict:
        """验证时间点"""
        return self._handler.validate_time_points(time_points, video_duration)
    
    # ==================== 废弃的方法（保留以防兼容性问题） ====================
    
    def _setup_ffmpeg_path(self):
        """已废弃：FFmpeg配置现在由BaseVideoHandler处理"""
        print("警告: _setup_ffmpeg_path方法已废弃，FFmpeg配置由BaseVideoHandler自动处理")
        pass