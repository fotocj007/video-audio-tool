#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视频音频合并模块
实现视频文件和音频文件的合并功能
"""

import os
import subprocess
from typing import Dict, Callable, Optional
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip
import traceback
from .base_handler import BaseVideoHandler

class VideoAudioMerger(BaseVideoHandler):
    """视频音频合并处理类"""
    
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
        try:
            # 测试FFmpeg配置
            if not self.test_ffmpeg_config():
                return {
                    'success': False,
                    'error': 'FFmpeg配置测试失败，请检查FFmpeg安装和配置'
                }
                
            if progress_callback:
                progress_callback(10)
                
            print(f"开始合并视频和音频: {video_path} + {audio_path}")
            
            # 验证输入文件
            if not os.path.exists(video_path):
                return {
                    'success': False,
                    'error': f'视频文件不存在: {video_path}'
                }
            
            if not os.path.exists(audio_path):
                return {
                    'success': False,
                    'error': f'音频文件不存在: {audio_path}'
                }
            
            if progress_callback:
                progress_callback(20)
            
            # 确保输出目录存在
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            # 首先尝试使用MoviePy合并
            try:
                with VideoFileClip(video_path) as video_clip, AudioFileClip(audio_path) as audio_clip:
                    if progress_callback:
                        progress_callback(40)
                    
                    # 调整音频长度以匹配视频
                    if audio_clip.duration > video_clip.duration:
                        audio_clip = audio_clip.subclip(0, video_clip.duration)
                    elif audio_clip.duration < video_clip.duration:
                        # 如果音频较短，可以选择循环或静音填充
                        print(f"警告: 音频长度({audio_clip.duration}s)短于视频长度({video_clip.duration}s)")
                    
                    if progress_callback:
                        progress_callback(60)
                    
                    # 根据replace_audio参数决定合并方式
                    if replace_audio:
                        # 替换原音频轨道
                        final_clip = video_clip.set_audio(audio_clip)
                    else:
                        # 混合音频轨道
                        if video_clip.audio is not None:
                            # 如果视频有音频，则混合
                            from moviepy.audio.fx import volumex
                            mixed_audio = CompositeAudioClip([video_clip.audio, audio_clip])
                            final_clip = video_clip.set_audio(mixed_audio)
                        else:
                            # 如果视频没有音频，直接设置
                            final_clip = video_clip.set_audio(audio_clip)
                    
                    if progress_callback:
                        progress_callback(80)
                    
                    # 写入输出文件
                    final_clip.write_videofile(
                        output_path,
                        codec='libx264',
                        audio_codec='aac',
                        verbose=False,
                        logger=None,
                        temp_audiofile=None,
                        remove_temp=True,
                        write_logfile=False,
                        threads=1
                    )
                    
                    final_clip.close()
                    
            except Exception as moviepy_error:
                print(f"MoviePy合并失败，尝试使用FFmpeg: {moviepy_error}")
                
                # 使用FFmpeg作为备选方案
                result = self._merge_with_ffmpeg(video_path, audio_path, output_path, replace_audio)
                if not result['success']:
                    raise Exception(f"FFmpeg合并也失败: {result['error']}")
            
            if progress_callback:
                progress_callback(100)
                
            print(f"视频音频合并完成: {output_path}")
            
            return {
                'success': True,
                'output_file': output_path,
                'message': '视频音频合并成功'
            }
            
        except Exception as e:
            error_msg = f"视频音频合并失败: {str(e)}"
            print(f"Error: {error_msg}")
            print(traceback.format_exc())
            return {
                'success': False,
                'error': error_msg
            }
    
    def _merge_with_ffmpeg(self, video_path: str, audio_path: str, output_path: str, replace_audio: bool = True) -> Dict:
        """
        使用FFmpeg合并视频和音频
        
        Args:
            video_path: 视频文件路径
            audio_path: 音频文件路径
            output_path: 输出文件路径
            replace_audio: 是否替换原音频轨道
            
        Returns:
            Dict: 包含成功状态或错误信息
        """
        try:
            ffmpeg_path = os.environ.get('FFMPEG_BINARY', 'ffmpeg')
            
            # 根据replace_audio参数构建FFmpeg命令
            if replace_audio:
                # 替换音频轨道
                cmd = [
                    ffmpeg_path,
                    '-i', video_path,
                    '-i', audio_path,
                    '-c:v', 'copy',  # 复制视频流，不重新编码
                    '-c:a', 'aac',   # 音频编码为AAC
                    '-map', '0:v:0', # 使用第一个输入的视频流
                    '-map', '1:a:0', # 使用第二个输入的音频流
                    '-shortest',     # 以较短的流为准
                    '-y',            # 覆盖输出文件
                    output_path
                ]
            else:
                # 混合音频轨道
                cmd = [
                    ffmpeg_path,
                    '-i', video_path,
                    '-i', audio_path,
                    '-c:v', 'copy',  # 复制视频流，不重新编码
                    '-filter_complex', '[0:a][1:a]amix=inputs=2[a]',  # 混合音频
                    '-map', '0:v:0', # 使用第一个输入的视频流
                    '-map', '[a]',   # 使用混合后的音频
                    '-c:a', 'aac',   # 音频编码为AAC
                    '-shortest',     # 以较短的流为准
                    '-y',            # 覆盖输出文件
                    output_path
                ]
            
            print(f"执行FFmpeg命令: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode != 0:
                return {
                    'success': False,
                    'error': f'FFmpeg执行失败: {result.stderr}'
                }
            
            return {
                'success': True,
                'message': 'FFmpeg合并成功'
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'FFmpeg执行超时（超过5分钟）'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'FFmpeg合并过程中发生错误: {str(e)}'
            }
    
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
        try:
            # 测试FFmpeg配置
            if not self.test_ffmpeg_config():
                return {
                    'success': False,
                    'error': 'FFmpeg配置测试失败，请检查FFmpeg安装和配置'
                }
                
            if progress_callback:
                progress_callback(10)
                
            print(f"开始替换视频音频: {video_path} -> {audio_path}")
            
            # 验证输入文件
            if not os.path.exists(video_path):
                return {
                    'success': False,
                    'error': f'视频文件不存在: {video_path}'
                }
            
            if not os.path.exists(audio_path):
                return {
                    'success': False,
                    'error': f'音频文件不存在: {audio_path}'
                }
            
            if progress_callback:
                progress_callback(30)
            
            # 确保输出目录存在
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            # 使用FFmpeg替换音频
            ffmpeg_path = os.environ.get('FFMPEG_BINARY', 'ffmpeg')
            
            cmd = [
                ffmpeg_path,
                '-i', video_path,
                '-i', audio_path,
                '-c:v', 'copy',  # 复制视频流
                '-c:a', 'aac',   # 重新编码音频
                '-map', '0:v',   # 使用视频文件的视频流
                '-map', '1:a',   # 使用音频文件的音频流
                '-shortest',     # 以较短的流为准
                '-y',            # 覆盖输出文件
                output_path
            ]
            
            if progress_callback:
                progress_callback(50)
            
            print(f"执行FFmpeg命令: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode != 0:
                return {
                    'success': False,
                    'error': f'音频替换失败: {result.stderr}'
                }
            
            if progress_callback:
                progress_callback(100)
                
            print(f"音频替换完成: {output_path}")
            
            return {
                'success': True,
                'output_file': output_path,
                'message': '音频替换成功'
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': '音频替换超时（超过5分钟）'
            }
        except Exception as e:
            error_msg = f"音频替换失败: {str(e)}"
            print(f"Error: {error_msg}")
            print(traceback.format_exc())
            return {
                'success': False,
                'error': error_msg
            }
    
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
        try:
            # 测试FFmpeg配置
            if not self.test_ffmpeg_config():
                return {
                    'success': False,
                    'error': 'FFmpeg配置测试失败，请检查FFmpeg安装和配置'
                }
                
            if progress_callback:
                progress_callback(10)
                
            print(f"开始移除视频音频: {video_path}")
            
            # 验证输入文件
            if not os.path.exists(video_path):
                return {
                    'success': False,
                    'error': f'视频文件不存在: {video_path}'
                }
            
            if progress_callback:
                progress_callback(30)
            
            # 确保输出目录存在
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            with VideoFileClip(video_path) as video_clip:
                if progress_callback:
                    progress_callback(50)
                    
                # 移除音频
                video_only = video_clip.without_audio()
                
                if progress_callback:
                    progress_callback(70)
                
                # 写入输出文件
                video_only.write_videofile(
                    output_path,
                    codec='libx264',
                    verbose=False,
                    logger=None,
                    write_logfile=False,
                    threads=1
                )
                
                video_only.close()
            
            if progress_callback:
                progress_callback(100)
                
            print(f"音频移除完成: {output_path}")
            
            return {
                'success': True,
                'output_file': output_path,
                'message': '音频移除成功'
            }
            
        except Exception as e:
            error_msg = f"音频移除失败: {str(e)}"
            print(f"Error: {error_msg}")
            print(traceback.format_exc())
            return {
                'success': False,
                'error': error_msg
            }