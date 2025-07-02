#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
音频提取模块
实现从视频文件中提取音频的功能
"""

import os
from typing import Dict, Callable, Optional
from moviepy.editor import VideoFileClip
import traceback
from .base_handler import BaseVideoHandler

class AudioExtractor(BaseVideoHandler):
    """音频提取处理类"""
    
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
        try:
            # 测试FFmpeg配置
            if not self.test_ffmpeg_config():
                return {
                    'success': False,
                    'error': 'FFmpeg配置测试失败，请检查FFmpeg安装和配置'
                }
                
            if progress_callback:
                progress_callback(10)
                
            print(f"开始从视频提取音频: {video_path}")
            
            with VideoFileClip(video_path) as video:
                if progress_callback:
                    progress_callback(30)
                    
                if video.audio is None:
                    return {
                        'success': False,
                        'error': '视频文件不包含音频轨道'
                    }
                
                if progress_callback:
                    progress_callback(50)
                    
                # 确保输出目录存在
                output_dir = os.path.dirname(output_path)
                if output_dir and not os.path.exists(output_dir):
                    os.makedirs(output_dir)
                
                # 提取音频
                video.audio.write_audiofile(
                    output_path,
                    verbose=False,
                    logger=None,
                    write_logfile=False
                )
                
                if progress_callback:
                    progress_callback(100)
                    
                print(f"音频提取完成: {output_path}")
                
                return {
                    'success': True,
                    'output_file': output_path,
                    'message': '音频提取成功'
                }
                
        except Exception as e:
            error_msg = f"音频提取失败: {str(e)}"
            print(f"Error: {error_msg}")
            print(traceback.format_exc())
            return {
                'success': False,
                'error': error_msg
            }
    
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
        try:
            # 测试FFmpeg配置
            if not self.test_ffmpeg_config():
                return {
                    'success': False,
                    'error': 'FFmpeg配置测试失败，请检查FFmpeg安装和配置'
                }
                
            if progress_callback:
                progress_callback(10)
                
            print(f"开始提取音频片段: {video_path} ({start_time}s - {end_time}s)")
            
            with VideoFileClip(video_path) as video:
                if progress_callback:
                    progress_callback(30)
                    
                if video.audio is None:
                    return {
                        'success': False,
                        'error': '视频文件不包含音频轨道'
                    }
                
                # 验证时间范围
                if start_time < 0 or end_time > video.duration or start_time >= end_time:
                    return {
                        'success': False,
                        'error': f'无效的时间范围: {start_time}s - {end_time}s (视频总长度: {video.duration}s)'
                    }
                
                if progress_callback:
                    progress_callback(50)
                    
                # 确保输出目录存在
                output_dir = os.path.dirname(output_path)
                if output_dir and not os.path.exists(output_dir):
                    os.makedirs(output_dir)
                
                # 提取音频片段
                audio_segment = video.audio.subclip(start_time, end_time)
                audio_segment.write_audiofile(
                    output_path,
                    verbose=False,
                    logger=None,
                    write_logfile=False
                )
                audio_segment.close()
                
                if progress_callback:
                    progress_callback(100)
                    
                print(f"音频片段提取完成: {output_path}")
                
                return {
                    'success': True,
                    'output_file': output_path,
                    'message': f'音频片段提取成功 ({start_time}s - {end_time}s)'
                }
                
        except Exception as e:
            error_msg = f"音频片段提取失败: {str(e)}"
            print(f"Error: {error_msg}")
            print(traceback.format_exc())
            return {
                'success': False,
                'error': error_msg
            }
    
    def get_audio_info(self, video_path: str) -> Dict:
        """
        获取视频文件的音频信息
        
        Args:
            video_path: 视频文件路径
            
        Returns:
            Dict: 包含音频信息或错误信息
        """
        try:
            with VideoFileClip(video_path) as video:
                if video.audio is None:
                    return {
                        'success': True,
                        'has_audio': False,
                        'message': '视频文件不包含音频轨道'
                    }
                
                audio_info = {
                    'success': True,
                    'has_audio': True,
                    'duration': video.audio.duration,
                    'fps': video.audio.fps if hasattr(video.audio, 'fps') else None,
                    'nchannels': video.audio.nchannels if hasattr(video.audio, 'nchannels') else None
                }
                
                return audio_info
                
        except Exception as e:
            error_msg = f"获取音频信息失败: {str(e)}"
            print(f"Error: {error_msg}")
            return {
                'success': False,
                'error': error_msg
            }