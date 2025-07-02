#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础视频处理类
包含所有视频处理模块的共用功能
"""

import os
import subprocess
from typing import Optional

# 安全导入moviepy配置
try:
    from moviepy.config import FFMPEG_BINARY, FFPROBE_BINARY
except ImportError:
    # 如果导入失败，使用默认值
    FFMPEG_BINARY = 'ffmpeg'
    FFPROBE_BINARY = 'ffprobe'

class BaseVideoHandler:
    """视频处理基础类"""
    
    def __init__(self):
        """初始化视频处理器"""
        try:
            # 设置FFmpeg路径
            self._setup_ffmpeg_path()
            
            # 验证FFmpeg配置
            if not self.test_ffmpeg_config():
                print("警告: FFmpeg配置验证失败，尝试重置为系统默认值")
                # 尝试重置为系统默认值
                try:
                    import moviepy.config
                    moviepy.config.FFMPEG_BINARY = 'ffmpeg'
                    moviepy.config.FFPROBE_BINARY = 'ffprobe'
                    os.environ['FFMPEG_BINARY'] = 'ffmpeg'
                    os.environ['FFPROBE_BINARY'] = 'ffprobe'
                except Exception as reset_error:
                    print(f"重置FFmpeg配置失败: {reset_error}")
                    
        except Exception as init_error:
            print(f"初始化FFmpeg配置时发生错误: {init_error}")
            # 继续初始化，但用户需要手动配置FFmpeg
    
    def _setup_ffmpeg_path(self):
        """设置FFmpeg路径"""
        try:
            # 获取项目根目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)
            
            # FFmpeg可执行文件路径
            ffmpeg_path = os.path.join(project_root, 'ffmpeg.exe')
            ffprobe_path = os.path.join(project_root, 'ffprobe.exe')
            
            # 设置环境变量以确保FFmpeg能被找到
            if os.path.exists(ffmpeg_path):
                os.environ['FFMPEG_BINARY'] = ffmpeg_path
                # 尝试设置moviepy配置
                try:
                    import moviepy.config
                    moviepy.config.FFMPEG_BINARY = ffmpeg_path
                except Exception:
                    pass
                print(f"FFmpeg路径设置为: {ffmpeg_path}")
            else:
                raise FileNotFoundError(f"FFmpeg可执行文件未找到: {ffmpeg_path}")
                
            if os.path.exists(ffprobe_path):
                os.environ['FFPROBE_BINARY'] = ffprobe_path
                # 尝试设置moviepy配置
                try:
                    import moviepy.config
                    moviepy.config.FFPROBE_BINARY = ffprobe_path
                except Exception:
                    pass
                print(f"FFprobe路径设置为: {ffprobe_path}")
            else:
                raise FileNotFoundError(f"FFprobe可执行文件未找到: {ffprobe_path}")
                
        except Exception as e:
            print(f"FFmpeg路径配置失败: {e}")
            raise
    
    def test_ffmpeg_config(self) -> bool:
        """
        测试FFmpeg配置是否正确
        
        Returns:
            bool: 配置是否正确
        """
        try:
            # 获取FFmpeg路径
            ffmpeg_path = os.environ.get('FFMPEG_BINARY', 'ffmpeg')
            
            # 检查文件是否存在（如果是完整路径）
            if os.path.isabs(ffmpeg_path) and not os.path.exists(ffmpeg_path):
                print(f"FFmpeg文件不存在: {ffmpeg_path}")
                return False
            
            # 尝试运行FFmpeg版本命令
            result = subprocess.run(
                [ffmpeg_path, '-version'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                print("FFmpeg配置测试通过")
                return True
            else:
                print(f"FFmpeg配置测试失败: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("FFmpeg配置测试超时")
            return False
        except FileNotFoundError:
            print("FFmpeg可执行文件未找到")
            return False
        except Exception as e:
            print(f"FFmpeg配置测试异常: {e}")
            return False
    
    def _time_str_to_seconds(self, time_str: str) -> float:
        """
        将时间字符串转换为秒数
        
        Args:
            time_str: 时间字符串，格式为 HH:MM:SS 或 MM:SS 或 SS
            
        Returns:
            float: 秒数
        """
        try:
            parts = time_str.split(':')
            if len(parts) == 3:  # HH:MM:SS
                hours, minutes, seconds = map(float, parts)
                return hours * 3600 + minutes * 60 + seconds
            elif len(parts) == 2:  # MM:SS
                minutes, seconds = map(float, parts)
                return minutes * 60 + seconds
            elif len(parts) == 1:  # SS
                return float(parts[0])
            else:
                raise ValueError(f"无效的时间格式: {time_str}")
        except ValueError as e:
            print(f"时间格式转换错误: {e}")
            return 0.0
    
    def _seconds_to_time_str(self, seconds: float) -> str:
        """
        将秒数转换为时间字符串
        
        Args:
            seconds: 秒数
            
        Returns:
            str: 时间字符串，格式为 HH:MM:SS
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{secs:06.3f}"
    
    def get_video_info(self, video_path: str) -> dict:
        """
        获取视频文件信息
        
        Args:
            video_path: 视频文件路径
            
        Returns:
            dict: 视频信息
        """
        try:
            from moviepy.editor import VideoFileClip
            
            with VideoFileClip(video_path) as video:
                # 基础信息
                duration = video.duration
                fps = video.fps
                size = video.size
                
                info = {
                    'success': True,
                    'duration': duration,
                    'fps': fps,
                    'size': size,
                    'has_audio': video.audio is not None,
                    # 添加格式化字段以保持向后兼容
                    'duration_str': self._seconds_to_time_str(duration),
                    'size_str': f"{size[0]}x{size[1]}" if size else "未知"
                }
                
                if video.audio is not None:
                    info['audio_duration'] = video.audio.duration
                    info['audio_fps'] = getattr(video.audio, 'fps', None)
                    info['audio_channels'] = getattr(video.audio, 'nchannels', None)
                
                return info
                
        except Exception as e:
            return {
                'success': False,
                'error': f'获取视频信息失败: {str(e)}'
            }
    
    def validate_file_path(self, file_path: str, file_type: str = "文件") -> bool:
        """
        验证文件路径是否有效
        
        Args:
            file_path: 文件路径
            file_type: 文件类型描述
            
        Returns:
            bool: 路径是否有效
        """
        if not file_path:
            print(f"错误: {file_type}路径为空")
            return False
            
        if not os.path.exists(file_path):
            print(f"错误: {file_type}不存在: {file_path}")
            return False
            
        if not os.path.isfile(file_path):
            print(f"错误: {file_path} 不是一个文件")
            return False
            
        return True
    
    def ensure_output_dir(self, output_path: str) -> bool:
        """
        确保输出目录存在
        
        Args:
            output_path: 输出文件路径
            
        Returns:
            bool: 目录创建是否成功
        """
        try:
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
                print(f"创建输出目录: {output_dir}")
            return True
        except Exception as e:
            print(f"创建输出目录失败: {e}")
            return False