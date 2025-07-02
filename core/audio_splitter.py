# -*- coding: utf-8 -*-
"""
音频拆分核心模块
实现音频文件拆分功能
"""

import os
import subprocess
from typing import List, Dict, Callable, Optional

try:
    from pydub import AudioSegment
except ImportError:
    AudioSegment = None
    print("Warning: pydub not installed")


class AudioSplitter:
    """音频拆分处理类"""
    
    def __init__(self):
        """初始化音频拆分器"""
        # 初始化路径属性
        self.ffmpeg_path = None
        self.ffprobe_path = None
        # 配置ffmpeg路径
        self._setup_ffmpeg_path()
        
    def _setup_ffmpeg_path(self):
        """设置ffmpeg路径"""
        try:
            # 获取项目根目录的ffmpeg.exe路径
            current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            ffmpeg_path = os.path.join(current_dir, "ffmpeg.exe")
            ffprobe_path = os.path.join(current_dir, "ffprobe.exe")
            
            if os.path.exists(ffmpeg_path):
                # 设置实例属性
                self.ffmpeg_path = ffmpeg_path
                self.ffprobe_path = ffprobe_path
                
                # 如果pydub可用，也配置pydub
                if AudioSegment is not None:
                    # 设置环境变量，让pydub能找到ffmpeg
                    os.environ['PATH'] = current_dir + os.pathsep + os.environ.get('PATH', '')
                    
                    # 设置pydub的ffmpeg路径属性
                    AudioSegment.converter = ffmpeg_path
                    AudioSegment.ffmpeg = ffmpeg_path
                    AudioSegment.ffprobe = ffprobe_path 
                    
                    # 强制设置pydub内部的路径缓存
                    import pydub.utils
                    pydub.utils._which_cache = {}
                    pydub.utils._which_cache['ffmpeg'] = ffmpeg_path
                    pydub.utils._which_cache['ffprobe'] = ffprobe_path

                print(f"已配置ffmpeg路径: {ffmpeg_path}")
                print(f"已配置ffprobe路径: {ffprobe_path}")
            else:
                print(f"警告: 未找到ffmpeg.exe文件: {ffmpeg_path}")
        except Exception as e:
            print(f"配置ffmpeg路径时出错: {str(e)}")
            
    def split_audio(self, audio_path: str, time_points: List[str],
                   output_dir: str, progress_callback: Optional[Callable] = None) -> Dict:
        """
        拆分音频文件
        
        Args:
            audio_path: 音频文件路径
            time_points: 拆分时间点列表 (格式: HH:MM:SS)
            output_dir: 输出目录
            progress_callback: 进度回调函数
            
        Returns:
            Dict: 包含成功状态、输出文件列表或错误信息
        """
        try:
            # 优先使用FFmpeg命令行进行快速拆分
            return self._split_audio_with_ffmpeg(audio_path, time_points, output_dir, progress_callback)
        except Exception as e:
            print(f"FFmpeg拆分失败，尝试使用pydub: {str(e)}")
            # 如果FFmpeg失败，回退到pydub方法
            return self._split_audio_with_pydub(audio_path, time_points, output_dir, progress_callback)
    
    def _split_audio_with_ffmpeg(self, audio_path: str, time_points: List[str],
                                output_dir: str, progress_callback: Optional[Callable] = None) -> Dict:
        """
        使用FFmpeg命令行快速拆分音频
        """
        if progress_callback:
            progress_callback(10)
            
        # 获取FFmpeg路径
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        ffmpeg_path = os.path.join(current_dir, "ffmpeg.exe")
        
        if not os.path.exists(ffmpeg_path):
            raise Exception("找不到ffmpeg.exe")
            
        # 获取音频总时长
        ffprobe_path = os.path.join(current_dir, "ffprobe.exe")
        duration_cmd = [
            ffprobe_path, "-v", "quiet", "-show_entries", "format=duration", 
            "-of", "csv=p=0", audio_path
        ]
        
        try:
            result = subprocess.run(duration_cmd, capture_output=True, text=True, check=True)
            total_duration = float(result.stdout.strip())
        except:
            raise Exception("无法获取音频时长")
            
        if progress_callback:
            progress_callback(20)
            
        # 转换时间点为秒并排序
        time_seconds = []
        invalid_points = []
        for time_str in time_points:
            seconds = self._time_str_to_seconds(time_str)
            if 0 < seconds < total_duration:  # 排除0和总时长，避免重复
                time_seconds.append(seconds)
            elif seconds >= total_duration:
                invalid_points.append(f"{time_str}({seconds:.2f}s)")
                
        if invalid_points:
            print(f"警告：以下拆分点超出音频时长({total_duration:.2f}s)，已忽略: {', '.join(invalid_points)}")
                
        time_seconds.sort()
        
        # 去除重复的时间点
        time_seconds = list(dict.fromkeys(time_seconds))  # 保持顺序的去重
        
        # 检查是否有有效的拆分点
        if not time_seconds:
            raise Exception(f"没有有效的拆分点。音频时长为{total_duration:.2f}秒，请确保拆分点在0到{total_duration:.2f}秒之间。")
        
        # 添加开始和结束时间点
        split_points = [0] + time_seconds + [total_duration]
        
        # 调试信息：打印拆分点
        print(f"拆分点: {split_points}")
        print(f"将生成 {len(split_points) - 1} 个音频片段")
        
        if progress_callback:
            progress_callback(30)
            
        # 确保输出目录存在并检查写入权限
        try:
            os.makedirs(output_dir, exist_ok=True)
            # 测试写入权限
            test_file = os.path.join(output_dir, '.write_test')
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
        except PermissionError:
            raise Exception(f"没有权限写入输出目录: {output_dir}")
        except Exception as e:
            raise Exception(f"无法创建或访问输出目录: {str(e)}")
            
        # 生成输出文件列表
        output_files = []
        base_name = os.path.splitext(os.path.basename(audio_path))[0]
        file_extension = os.path.splitext(audio_path)[1]
        
        # 使用FFmpeg拆分音频
        for i in range(len(split_points) - 1):
            start_time = split_points[i]
            duration = split_points[i + 1] - start_time
            
            # 生成输出文件名
            output_filename = f"{base_name}_part_{i+1:02d}{file_extension}"
            output_path = os.path.normpath(os.path.join(output_dir, output_filename))
            
            # FFmpeg命令：使用-c copy进行快速拆分，不重新编码
            cmd = [
                ffmpeg_path,
                "-i", audio_path,
                "-ss", str(start_time),
                "-t", str(duration),
                "-c", "copy",  # 复制流，不重新编码
                "-avoid_negative_ts", "make_zero",
                "-y",  # 覆盖输出文件
                output_path
            ]
            
            # 执行FFmpeg命令
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                output_files.append(output_path)
            else:
                raise Exception(f"FFmpeg拆分失败: {result.stderr}")
                
            # 更新进度
            if progress_callback:
                progress = 30 + (i + 1) * 60 // len(split_points)
                progress_callback(progress)
                
        if progress_callback:
            progress_callback(100)
            
        return {
            'success': True,
            'output_files': output_files,
            'message': f'音频拆分完成，生成了 {len(output_files)} 个文件'
        }
        
    def _split_audio_with_pydub(self, audio_path: str, time_points: List[str],
                               output_dir: str, progress_callback: Optional[Callable] = None) -> Dict:
        """
        使用pydub拆分音频（备用方法）
        """
        if AudioSegment is None:
            raise Exception("pydub未安装，无法使用备用拆分方法")
            
        try:
            if progress_callback:
                progress_callback(10)
                
            # 加载音频
            audio = AudioSegment.from_file(audio_path)
            total_duration_ms = len(audio)
            
            if progress_callback:
                progress_callback(20)
                
            # 转换时间点为毫秒并排序
            time_ms = []
            invalid_points = []
            for time_str in time_points:
                ms = self._time_str_to_milliseconds(time_str)
                if 0 < ms < total_duration_ms:  # 排除0和总时长，避免重复
                    time_ms.append(ms)
                elif ms >= total_duration_ms:
                    invalid_points.append(f"{time_str}({ms/1000:.2f}s)")
                    
            if invalid_points:
                print(f"警告：以下拆分点超出音频时长({total_duration_ms/1000:.2f}s)，已忽略: {', '.join(invalid_points)}")
                    
            time_ms.sort()
            
            # 去除重复的时间点
            time_ms = list(dict.fromkeys(time_ms))  # 保持顺序的去重
            
            # 检查是否有有效的拆分点
            if not time_ms:
                raise Exception(f"没有有效的拆分点。音频时长为{total_duration_ms/1000:.2f}秒，请确保拆分点在0到{total_duration_ms/1000:.2f}秒之间。")
            
            # 添加开始和结束时间点
            split_points = [0] + time_ms + [total_duration_ms]
            
            # 调试信息：打印拆分点
            print(f"拆分点(毫秒): {split_points}")
            print(f"将生成 {len(split_points) - 1} 个音频片段")
            
            if progress_callback:
                progress_callback(30)
                
            # 确保输出目录存在并检查写入权限
            try:
                os.makedirs(output_dir, exist_ok=True)
                # 测试写入权限
                test_file = os.path.join(output_dir, '.write_test')
                with open(test_file, 'w') as f:
                    f.write('test')
                os.remove(test_file)
            except PermissionError:
                raise Exception(f"没有权限写入输出目录: {output_dir}")
            except Exception as e:
                raise Exception(f"无法创建或访问输出目录: {str(e)}")
                
            # 生成输出文件列表
            output_files = []
            base_name = os.path.splitext(os.path.basename(audio_path))[0]
            file_extension = os.path.splitext(audio_path)[1]
            
            # 拆分音频
            for i in range(len(split_points) - 1):
                start_ms = split_points[i]
                end_ms = split_points[i + 1]
                
                # 创建子片段
                segment = audio[start_ms:end_ms]
                
                # 生成输出文件名
                output_filename = f"{base_name}_part_{i+1:02d}{file_extension}"
                output_path = os.path.normpath(os.path.join(output_dir, output_filename))
                
                # 导出文件
                segment.export(output_path, format=file_extension[1:] if file_extension else "mp3")
                output_files.append(output_path)
                
                # 更新进度
                if progress_callback:
                    progress = 30 + (i + 1) * 60 // len(split_points)
                    progress_callback(progress)
                        
            if progress_callback:
                progress_callback(100)
                
            return {
                'success': True,
                'output_files': output_files,
                'message': f'音频拆分完成，生成了 {len(output_files)} 个文件'
            }
            
        except Exception as e:
            error_msg = f"音频拆分失败: {str(e)}"
            print(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
            
    def get_audio_info(self, audio_path: str) -> Dict:
        """
        获取音频信息
        
        Args:
            audio_path: 音频文件路径
            
        Returns:
            Dict: 包含音频信息的字典
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(audio_path):
                return {
                    'success': False,
                    'error': f'文件不存在: {audio_path}'
                }
                
            # 获取基本信息
            basic_info = self._get_basic_audio_info(audio_path)
            
            if basic_info['success']:
                # 添加格式化字符串
                duration = basic_info['duration']
                channels = basic_info['channels']
                sample_rate = basic_info['sample_rate']
                
                # 格式化时长
                hours = int(duration // 3600)
                minutes = int((duration % 3600) // 60)
                seconds = int(duration % 60)
                duration_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                
                # 格式化声道信息
                if channels == 1:
                    channels_str = "单声道"
                elif channels == 2:
                    channels_str = "立体声"
                else:
                    channels_str = f"{channels}声道"
                
                # 格式化采样率
                sample_rate_str = f"{sample_rate}Hz"
                
                # 添加格式化字段到结果中
                basic_info['duration_str'] = duration_str
                basic_info['channels_str'] = channels_str
                basic_info['sample_rate_str'] = sample_rate_str
                
                return basic_info
            else:
                # 如果基本方法失败，尝试使用pydub
                if AudioSegment is not None:
                    try:
                        audio = AudioSegment.from_file(audio_path)
                        duration_seconds = len(audio) / 1000.0
                        channels = audio.channels
                        sample_rate = audio.frame_rate
                        
                        # 格式化时长
                        hours = int(duration_seconds // 3600)
                        minutes = int((duration_seconds % 3600) // 60)
                        seconds = int(duration_seconds % 60)
                        duration_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                        
                        # 格式化声道信息
                        if channels == 1:
                            channels_str = "单声道"
                        elif channels == 2:
                            channels_str = "立体声"
                        else:
                            channels_str = f"{channels}声道"
                        
                        # 格式化采样率
                        sample_rate_str = f"{sample_rate}Hz"
                        
                        return {
                            'success': True,
                            'duration': duration_seconds,
                            'channels': channels,
                            'sample_rate': sample_rate,
                            'format': os.path.splitext(audio_path)[1][1:].upper(),
                            'duration_str': duration_str,
                            'channels_str': channels_str,
                            'sample_rate_str': sample_rate_str
                        }
                    except Exception as e:
                        return {
                            'success': False,
                            'error': f'无法读取音频文件: {str(e)}'
                        }
                else:
                    return basic_info
                    
        except Exception as e:
            return {
                'success': False,
                'error': f'获取音频信息失败: {str(e)}'
            }
            
    def _get_basic_audio_info(self, audio_path: str) -> Dict:
        """
        使用ffprobe获取基本音频信息
        """
        try:
            current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            ffprobe_path = os.path.join(current_dir, "ffprobe.exe")
            
            if not os.path.exists(ffprobe_path):
                return {
                    'success': False,
                    'error': '找不到ffprobe.exe'
                }
                
            # 获取音频信息的命令
            cmd = [
                ffprobe_path,
                "-v", "quiet",
                "-print_format", "json",
                "-show_format",
                "-show_streams",
                audio_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            import json
            info = json.loads(result.stdout)
            
            # 提取音频流信息
            audio_stream = None
            for stream in info.get('streams', []):
                if stream.get('codec_type') == 'audio':
                    audio_stream = stream
                    break
                    
            if audio_stream is None:
                return {
                    'success': False,
                    'error': '未找到音频流'
                }
                
            duration = float(info.get('format', {}).get('duration', 0))
            channels = int(audio_stream.get('channels', 0))
            sample_rate = int(audio_stream.get('sample_rate', 0))
            codec = audio_stream.get('codec_name', 'unknown')
            
            return {
                'success': True,
                'duration': duration,
                'channels': channels,
                'sample_rate': sample_rate,
                'format': codec.upper()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'获取音频信息失败: {str(e)}'
            }
            
    def _time_str_to_seconds(self, time_str: str) -> float:
        """
        将时间字符串转换为秒
        
        Args:
            time_str: 时间字符串 (HH:MM:SS)
            
        Returns:
            float: 秒数
        """
        try:
            parts = time_str.split(':')
            if len(parts) != 3:
                raise ValueError("时间格式错误")
                
            hours, minutes, seconds = map(float, parts)
            total_seconds = hours * 3600 + minutes * 60 + seconds
            return float(total_seconds)
        except Exception as e:
            print(f"时间转换错误: {str(e)}")
            return 0.0
            
    def _time_str_to_milliseconds(self, time_str: str) -> int:
        """
        将时间字符串转换为毫秒数
        
        Args:
            time_str: 时间字符串，格式为 HH:MM:SS 或 MM:SS 或 SS
            
        Returns:
            int: 毫秒数
        """
        seconds = self._time_str_to_seconds(time_str)
        return int(seconds * 1000)
        
    def _milliseconds_to_time_str(self, milliseconds: int) -> str:
        """
        将毫秒转换为时间字符串
        
        Args:
            milliseconds: 毫秒数
            
        Returns:
            str: 时间字符串 (HH:MM:SS)
        """
        total_seconds = milliseconds / 1000.0
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        seconds = int(total_seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"