#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一视频处理器
整合所有视频处理功能的统一接口
"""

from typing import List, Dict, Callable, Optional
from .video_splitter import VideoSplitter
from .audio_extractor import AudioExtractor
from .video_audio_merger import VideoAudioMerger
from .base_handler import BaseVideoHandler

class UnifiedVideoHandler(BaseVideoHandler):
    """统一视频处理器类"""
    
    def __init__(self):
        """初始化统一视频处理器"""
        super().__init__()
        
        # 初始化各个功能模块
        self.splitter = VideoSplitter()
        self.audio_extractor = AudioExtractor()
        self.merger = VideoAudioMerger()
    
    # ==================== 视频拆分功能 ====================
    
    def split_video(self, video_path: str, time_points: List[str], 
                   output_dir: str, progress_callback: Optional[Callable] = None) -> Dict:
        """
        拆分视频文件
        
        Args:
            video_path: 视频文件路径
            time_points: 拆分时间点列表 (格式: HH:MM:SS)
            output_dir: 输出目录
            progress_callback: 进度回调函数
            
        Returns:
            Dict: 包含成功状态、输出文件列表或错误信息
        """
        return self.splitter.split_video(video_path, time_points, output_dir, progress_callback)
    
    # ==================== 音频提取功能 ====================
    
    def extract_audio(self, video_path: str, output_path: str, 
                     audio_format: str = 'mp3', progress_callback: Optional[Callable] = None) -> Dict:
        """
        从视频文件中提取音频
        
        Args:
            video_path: 视频文件路径
            output_path: 输出音频文件路径
            audio_format: 音频格式 (mp3, wav, aac)
            progress_callback: 进度回调函数
            
        Returns:
            Dict: 包含成功状态、输出文件路径或错误信息
        """
        return self.audio_extractor.extract_audio(video_path, output_path, audio_format, progress_callback)
    
    def extract_audio_segment(self, video_path: str, output_path: str,
                            start_time: float, end_time: float,
                            progress_callback: Optional[Callable] = None) -> Dict:
        """
        从视频文件中提取指定时间段的音频
        
        Args:
            video_path: 视频文件路径
            output_path: 输出音频文件路径
            start_time: 开始时间（秒）
            end_time: 结束时间（秒）
            progress_callback: 进度回调函数
            
        Returns:
            Dict: 包含成功状态、输出文件路径或错误信息
        """
        return self.audio_extractor.extract_audio_segment(
            video_path, output_path, start_time, end_time, progress_callback
        )
    
    def get_audio_info(self, video_path: str) -> Dict:
        """
        获取视频文件的音频信息
        
        Args:
            video_path: 视频文件路径
            
        Returns:
            Dict: 包含音频信息或错误信息
        """
        return self.audio_extractor.get_audio_info(video_path)
    
    # ==================== 视频音频合并功能 ====================
    
    def merge_video_audio(self, video_path: str, audio_path: str, output_path: str,
                         replace_audio: bool = True, progress_callback: Optional[Callable] = None) -> Dict:
        """
        合并视频文件和音频文件
        
        Args:
            video_path: 视频文件路径
            audio_path: 音频文件路径
            output_path: 输出文件路径
            replace_audio: 是否替换原音频轨道
            progress_callback: 进度回调函数
            
        Returns:
            Dict: 包含成功状态、输出文件路径或错误信息
        """
        return self.merger.merge_video_audio(video_path, audio_path, output_path, replace_audio, progress_callback)
    
    def replace_audio(self, video_path: str, audio_path: str, output_path: str,
                     progress_callback: Optional[Callable] = None) -> Dict:
        """
        替换视频文件的音频轨道
        
        Args:
            video_path: 视频文件路径
            audio_path: 新音频文件路径
            output_path: 输出文件路径
            progress_callback: 进度回调函数
            
        Returns:
            Dict: 包含成功状态、输出文件路径或错误信息
        """
        return self.merger.replace_audio(video_path, audio_path, output_path, progress_callback)
    
    def remove_audio(self, video_path: str, output_path: str,
                    progress_callback: Optional[Callable] = None) -> Dict:
        """
        移除视频文件的音频轨道
        
        Args:
            video_path: 视频文件路径
            output_path: 输出文件路径
            progress_callback: 进度回调函数
            
        Returns:
            Dict: 包含成功状态、输出文件路径或错误信息
        """
        return self.merger.remove_audio(video_path, output_path, progress_callback)
    
    # ==================== 批量处理功能 ====================
    
    def batch_split_videos(self, video_configs: List[Dict], 
                          progress_callback: Optional[Callable] = None) -> Dict:
        """
        批量拆分视频文件
        
        Args:
            video_configs: 视频配置列表，每个配置包含:
                - video_path: 视频文件路径
                - time_points: 拆分时间点列表
                - output_dir: 输出目录
            progress_callback: 进度回调函数
            
        Returns:
            Dict: 包含批量处理结果
        """
        results = []
        total_videos = len(video_configs)
        
        for i, config in enumerate(video_configs):
            print(f"处理视频 {i+1}/{total_videos}: {config['video_path']}")
            
            result = self.split_video(
                config['video_path'],
                config['time_points'],
                config['output_dir']
            )
            
            results.append({
                'video_path': config['video_path'],
                'result': result
            })
            
            if progress_callback:
                progress = int((i + 1) / total_videos * 100)
                progress_callback(progress)
        
        # 统计结果
        successful = sum(1 for r in results if r['result']['success'])
        failed = total_videos - successful
        
        return {
            'success': failed == 0,
            'total': total_videos,
            'successful': successful,
            'failed': failed,
            'results': results,
            'message': f'批量处理完成: 成功 {successful}/{total_videos}'
        }
    
    def batch_extract_audio(self, video_audio_configs: List[Dict],
                           progress_callback: Optional[Callable] = None) -> Dict:
        """
        批量提取音频
        
        Args:
            video_audio_configs: 配置列表，每个配置包含:
                - video_path: 视频文件路径
                - output_path: 输出音频文件路径
            progress_callback: 进度回调函数
            
        Returns:
            Dict: 包含批量处理结果
        """
        results = []
        total_videos = len(video_audio_configs)
        
        for i, config in enumerate(video_audio_configs):
            print(f"提取音频 {i+1}/{total_videos}: {config['video_path']}")
            
            result = self.extract_audio(
                config['video_path'],
                config['output_path']
            )
            
            results.append({
                'video_path': config['video_path'],
                'result': result
            })
            
            if progress_callback:
                progress = int((i + 1) / total_videos * 100)
                progress_callback(progress)
        
        # 统计结果
        successful = sum(1 for r in results if r['result']['success'])
        failed = total_videos - successful
        
        return {
            'success': failed == 0,
            'total': total_videos,
            'successful': successful,
            'failed': failed,
            'results': results,
            'message': f'批量音频提取完成: 成功 {successful}/{total_videos}'
        }
    
    # ==================== 工具方法 ====================
    
    def get_supported_formats(self) -> Dict:
        """
        获取支持的文件格式
        
        Returns:
            Dict: 支持的格式信息
        """
        return {
            'video_input': ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm'],
            'video_output': ['.mp4', '.avi', '.mov', '.mkv'],
            'audio_input': ['.mp3', '.wav', '.aac', '.flac', '.ogg'],
            'audio_output': ['.mp3', '.wav', '.aac', '.flac']
        }
    
    def validate_time_points(self, time_points: List[str], video_duration: float) -> Dict:
        """
        验证时间点是否有效
        
        Args:
            time_points: 时间点列表
            video_duration: 视频总时长（秒）
            
        Returns:
            Dict: 验证结果
        """
        valid_points = []
        invalid_points = []
        
        for time_str in time_points:
            try:
                seconds = self._time_str_to_seconds(time_str)
                if 0 <= seconds <= video_duration:
                    valid_points.append(time_str)
                else:
                    invalid_points.append({
                        'time': time_str,
                        'reason': f'超出视频时长范围 (0-{video_duration:.2f}s)'
                    })
            except Exception as e:
                invalid_points.append({
                    'time': time_str,
                    'reason': f'时间格式错误: {str(e)}'
                })
        
        return {
            'valid': len(invalid_points) == 0,
            'valid_points': valid_points,
            'invalid_points': invalid_points,
            'message': f'有效时间点: {len(valid_points)}, 无效时间点: {len(invalid_points)}'
        }