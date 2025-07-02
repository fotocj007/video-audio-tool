#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视频拆分模块
实现视频文件的拆分功能
"""

import os
import subprocess
from typing import List, Dict, Callable, Optional
import traceback
from .base_handler import BaseVideoHandler

class VideoSplitter(BaseVideoHandler):
    """视频拆分处理类"""
    
    def split_video(self, video_path: str, time_points: List[str], 
                   output_dir: str, progress_callback: Optional[Callable] = None) -> Dict:
        """
        拆分视频文件 - 使用FFmpeg直接命令进行高效拆分
        
        Args:
            video_path: 视频文件路径
            time_points: 拆分时间点列表 (格式: HH:MM:SS)
            output_dir: 输出目录
            progress_callback: 进度回调函数
            
        Returns:
            Dict: 包含成功状态、输出文件列表或错误信息
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
                
            output_files = []
            base_name = os.path.splitext(os.path.basename(video_path))[0]
            ffmpeg_path = os.environ.get('FFMPEG_BINARY', 'ffmpeg')

            # 获取视频总时长
            total_duration = self._get_video_duration_ffmpeg(video_path)
            if total_duration is None:
                return {
                    'success': False,
                    'error': '无法获取视频时长信息'
                }

            if progress_callback: 
                progress_callback(20)

            # 转换时间点并排序
            time_seconds = sorted([
                s for s in (self._time_str_to_seconds(t) for t in time_points) 
                if 0 <= s <= total_duration
            ])
            split_points = [0] + time_seconds + [total_duration]
            intervals = list(zip(split_points[:-1], split_points[1:]))

            if progress_callback: 
                progress_callback(30)

            total_intervals = len(intervals)

            # 使用FFmpeg命令进行拆分
            for i, (start_time, end_time) in enumerate(intervals):
                if start_time >= end_time:
                    continue
                
                duration = end_time - start_time
                output_filename = f"{base_name}_part_{i+1:02d}.mp4"
                output_path = os.path.join(output_dir, output_filename)
                
                print(f"正在生成片段 {i+1}/{total_intervals}: {output_filename} ({start_time:.2f}s -> {end_time:.2f}s)")
                
                # 构建FFmpeg命令
                command = [
                    ffmpeg_path,
                    '-ss', str(start_time),   # 输入选项：快速定位到开始时间附近的关键帧
                    '-i', video_path,         # 输入文件
                    '-to', str(duration),     # 输出选项：从定位点开始，编码指定的时长
                    '-c:v', 'libx264',        # 视频重新编码，保证画面质量和兼容性
                    '-c:a', 'aac',            # 音频重新编码
                    '-y',                     # 覆盖已存在的文件
                    output_path               # 输出文件
                ]
                
                # 执行FFmpeg命令
                result = subprocess.run(command, capture_output=True, text=True, timeout=300)
                
                if result.returncode != 0:
                    print(f"FFmpeg执行失败: {result.stderr}")
                    return {
                        'success': False,
                        'error': f'片段 {i+1} 生成失败: {result.stderr}'
                    }
                
                output_files.append(output_path)
                
                if progress_callback:
                    progress = 30 + int((i + 1) / total_intervals * 60)
                    progress_callback(progress)
            
            if progress_callback: 
                progress_callback(100)

            return {
                'success': True,
                'output_files': output_files,
                'message': f'成功拆分为 {len(output_files)} 个文件'
            }
        except Exception as e:
            error_msg = f"视频拆分失败: {str(e)}"
            print(f"Error: {error_msg}")
            print(traceback.format_exc())
            return {
                'success': False,
                'error': error_msg
            }
    
    def _get_video_duration_ffmpeg(self, video_path: str) -> Optional[float]:
        """
        使用FFmpeg获取视频时长
        
        Args:
            video_path: 视频文件路径
            
        Returns:
            float: 视频时长（秒），如果获取失败返回None
        """
        try:
            ffprobe_path  = os.environ.get('FFPROBE_BINARY', 'ffprobe')
            command = [
                ffprobe_path ,
                '-v', 'error',                     # 只在发生错误时打印信息
                '-show_entries', 'format=duration',# 只请求格式信息中的时长
                '-of', 'default=noprint_wrappers=1:nokey=1', # 设置输出格式为纯数字
                video_path
            ]
            
            # 执行命令，ffprobe 几乎不会超时，但设置一个短超时是好习惯
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True,  # 如果 ffprobe 返回非0退出码，会抛出 CalledProcessError
                timeout=10   # 10秒对于 ffprobe 来说绰绰有余
            )
            
            # ffprobe 直接输出了秒数，转换为浮点数即可
            duration = float(result.stdout.strip())
            return duration
        except Exception as e:
            print(f"获取视频时长失败: {e}")
            return None