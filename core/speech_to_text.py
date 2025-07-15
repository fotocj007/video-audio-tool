# -*- coding: utf-8 -*-
"""
语音转文字核心模块
实现语音识别功能
"""

import os
from typing import Dict, Callable, Optional

from faster_whisper import WhisperModel

# try:
    # import whisper
# except ImportError:
#     whisper = None
#     print("Warning: whisper not installed")

try:
    from pydub import AudioSegment
except ImportError:
    AudioSegment = None
    print("Warning: pydub not installed")

try:
    from opencc import OpenCC
except ImportError:
    OpenCC = None
    print("Warning: opencc-python-reimplemented not installed")


class SpeechToText:
    """语音转文字处理类"""
    
    def __init__(self):
        """初始化语音转文字处理器"""
        self.whisper_model = None
        self.current_model_size = None
        self.opencc_converter = None
        self._setup_ffmpeg_path()
        self._setup_opencc()

        
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
            
    def _setup_opencc(self):
        """设置OpenCC繁体转简体转换器"""
        try:
            if OpenCC is not None:
                # 初始化繁体转简体转换器
                self.opencc_converter = OpenCC('t2s')  # traditional to simplified
                print("已配置OpenCC繁体转简体转换器")
            else:
                print("警告: opencc-python-reimplemented未安装，无法进行繁简转换")
        except Exception as e:
            print(f"配置OpenCC转换器时出错: {str(e)}")
            self.opencc_converter = None

    def speech_to_text(self, audio_path: str, output_path: str, 
                      model_size: str = 'base', progress_callback: Optional[Callable] = None) -> Dict:
        """
        语音转文字
        
        Args:
            audio_path: 音频文件路径
            output_path: 输出文本文件路径
            model_size: Whisper模型大小 (tiny, base, small, medium, large)
            progress_callback: 进度回调函数
            
        Returns:
            Dict: 包含成功状态、转录文本或错误信息
        """
        return self._transcribe_audio(audio_path, output_path, model_size, progress_callback, output_format='text')
    
    def speech_to_subtitle(self, audio_path: str, output_path: str, 
                          model_size: str = 'base', subtitle_format: str = 'srt',
                          progress_callback: Optional[Callable] = None) -> Dict:
        """
        语音转字幕文件
        
        Args:
            audio_path: 音频文件路径
            output_path: 输出字幕文件路径
            model_size: Whisper模型大小 (tiny, base, small, medium, large)
            subtitle_format: 字幕格式 ('srt', 'vtt', 'ass')
            progress_callback: 进度回调函数
            
        Returns:
            Dict: 包含成功状态、字幕内容或错误信息
        """
        return self._transcribe_audio(audio_path, output_path, model_size, progress_callback, 
                                    output_format='subtitle', subtitle_format=subtitle_format)
    
    def _transcribe_audio(self, audio_path: str, output_path: str, 
                          model_size: str = 'base', progress_callback: Optional[Callable] = None,
                          output_format: str = 'text', subtitle_format: str = 'srt') -> Dict:
        """
        音频转录核心方法
        
        Args:
            audio_path: 音频文件路径
            output_path: 输出文件路径
            model_size: Whisper模型大小 (tiny, base, small, medium, large)
            progress_callback: 进度回调函数
            output_format: 输出格式 ('text' 或 'subtitle')
            subtitle_format: 字幕格式 ('srt', 'vtt', 'ass')
            
        Returns:
            Dict: 包含成功状态、转录内容或错误信息
        """
        # if whisper is None:
        #     return {
        #         'success': False,
        #         'error': 'Whisper模块未安装，请运行: pip install openai-whisper'
        #     }
            
        # 预处理音频文件
        processed_audio_path = None
        temp_file_to_delete = None
        
        try:
            if progress_callback:
                progress_callback(10)
                
            print(f"语音转文字当前模型：{model_size}")
            # 加载或重新加载模型
            if self.whisper_model is None or self.current_model_size != model_size:
                if progress_callback:
                    progress_callback(20)
                    
                script_path = os.path.abspath(__file__)
                core_dir = os.path.dirname(script_path)
                project_root = os.path.dirname(core_dir)
                model_download_path = os.path.join(project_root, 'model', 'whisper')
                print(f"whisper 模型下载路径：{model_download_path}")

                os.makedirs(model_download_path, exist_ok=True)

                print(f"Loading Whisper model: {model_size}")
                # self.whisper_model = whisper.load_model(model_size,download_root=model_download_path)
                self.whisper_model = WhisperModel(model_size, compute_type="float32")
                self.current_model_size = model_size
                
            if progress_callback:
                progress_callback(40)
                
            processed_audio_path = self._preprocess_audio(audio_path)
            if processed_audio_path != audio_path:
                temp_file_to_delete = processed_audio_path
                
            if progress_callback:
                progress_callback(50)
                
            # 执行转录
            print(f"Transcribing audio: {processed_audio_path}")
            # result = self.whisper_model.transcribe(processed_audio_path, language="zh",temperature=0.0)
            segments, info = self.whisper_model.transcribe(processed_audio_path, language="zh", beam_size=5)
            
            if progress_callback:
                progress_callback(70)
            
            # 根据输出格式处理结果
            if output_format == 'text':
                # 提取转录文本
                transcribed_text = ""
                for segment in segments:
                    print(f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}")
                    transcribed_text += segment.text

                # 繁体转简体
                if self.opencc_converter is not None and transcribed_text:
                    try:
                        transcribed_text = self.opencc_converter.convert(transcribed_text)
                        print("已完成繁体转简体转换")
                    except Exception as e:
                        print(f"繁体转简体转换失败: {str(e)}")
                        # 转换失败时继续使用原文本
                
                # 保存到文件
                # 确保输出目录存在
                output_dir = os.path.dirname(output_path)
                if output_dir:
                    os.makedirs(output_dir, exist_ok=True)
                    
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(transcribed_text)
                    
                print(f"转录完成，文本已保存到: {output_path}")
                    
                if progress_callback:
                    progress_callback(100)
                    
                return {
                    'success': True,
                    'text': transcribed_text,
                    'output_path': output_path,
                    'message': '语音转文字完成'
                }
            
            elif output_format == 'subtitle':
                # 生成字幕文件
                subtitle_content = self._generate_subtitle(segments, subtitle_format)
                
                # 繁体转简体
                if self.opencc_converter is not None and subtitle_content:
                    try:
                        # 对于SRT和VTT格式，需要保留时间戳，只转换文本部分
                        if subtitle_format in ['srt', 'vtt']:
                            lines = subtitle_content.split('\n')
                            converted_lines = []
                            for line in lines:
                                # 跳过空行、数字行和时间戳行
                                if not line.strip() or line.strip().isdigit() or '-->' in line:
                                    converted_lines.append(line)
                                else:
                                    converted_lines.append(self.opencc_converter.convert(line))
                            subtitle_content = '\n'.join(converted_lines)
                        else:
                            # 对于其他格式，直接转换整个内容
                            subtitle_content = self.opencc_converter.convert(subtitle_content)
                        print("已完成繁体转简体转换")
                    except Exception as e:
                        print(f"繁体转简体转换失败: {str(e)}")
                        # 转换失败时继续使用原文本
                
                # 保存到文件
                # 确保输出目录存在
                output_dir = os.path.dirname(output_path)
                if output_dir:
                    os.makedirs(output_dir, exist_ok=True)
                
                # 确保文件扩展名正确
                base_name, _ = os.path.splitext(output_path)
                if subtitle_format == 'srt':
                    output_path = f"{base_name}.srt"
                elif subtitle_format == 'vtt':
                    output_path = f"{base_name}.vtt"
                elif subtitle_format == 'ass':
                    output_path = f"{base_name}.ass"
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(subtitle_content)
                
                print(f"字幕生成完成，已保存到: {output_path}")
                
                if progress_callback:
                    progress_callback(100)
                
                return {
                    'success': True,
                    'subtitle': subtitle_content,
                    'output_path': output_path,
                    'message': f'语音转{subtitle_format.upper()}字幕完成'
                }
            
            else:
                return {
                    'success': False,
                    'error': f'不支持的输出格式: {output_format}'
                }
                
        except Exception as e:
            error_msg = f"语音转文字失败: {str(e)}"
            print(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
        finally:
            # 确保无论成功还是失败，临时文件都会被删除
            if temp_file_to_delete and os.path.exists(temp_file_to_delete):
                try:
                    os.remove(temp_file_to_delete)
                    print(f"临时文件已删除: {temp_file_to_delete}")
                except Exception as e:
                    print(f"删除临时文件失败: {str(e)}")
            
    def _preprocess_audio(self, audio_path: str) -> str:
        """
        预处理音频文件，确保格式兼容
        
        Args:
            audio_path: 原始音频文件路径
            
        Returns:
            str: 处理后的音频文件路径
        """
        try:
            # 检查文件扩展名
            file_ext = os.path.splitext(audio_path)[1].lower()
            
            # Whisper支持的格式
            supported_formats = ['.mp3', '.wav', '.m4a', '.flac', '.ogg']
            
            if file_ext in supported_formats:
                # 如果是支持的格式，直接返回
                return audio_path
            else:
                # 如果不是支持的格式，转换为wav
                if AudioSegment is None:
                    print("警告: pydub未安装，无法转换音频格式")
                    return audio_path
                    
                print(f"转换音频格式: {file_ext} -> .wav")
                
                # 加载音频并转换为wav
                audio = AudioSegment.from_file(audio_path)
                
                # 生成临时文件路径
                temp_path = os.path.splitext(audio_path)[0] + '_temp.wav'
                
                # 导出为wav格式
                audio.export(temp_path, format="wav")
                
                return temp_path
                
        except Exception as e:
            print(f"音频预处理失败: {str(e)}")
            # 如果预处理失败，返回原始路径
            return audio_path
            
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
                
            # 使用pydub获取音频信息
            if AudioSegment is not None:
                try:
                    audio = AudioSegment.from_file(audio_path)
                    duration_seconds = len(audio) / 1000.0
                    
                    return {
                        'success': True,
                        'duration': duration_seconds,
                        'channels': audio.channels,
                        'sample_rate': audio.frame_rate,
                        'format': os.path.splitext(audio_path)[1][1:].upper()
                    }
                except Exception as e:
                    return {
                        'success': False,
                        'error': f'无法读取音频文件: {str(e)}'
                    }
            else:
                return {
                    'success': False,
                    'error': 'pydub未安装，无法获取音频信息'
                }
                    
        except Exception as e:
            return {
                'success': False,
                'error': f'获取音频信息失败: {str(e)}'
            }
    
    def _generate_subtitle(self, segments, subtitle_format: str) -> str:
        """
        生成字幕文件内容
        
        Args:
            segments: Whisper转录的片段列表
            subtitle_format: 字幕格式 ('srt', 'vtt', 'ass')
            
        Returns:
            str: 字幕文件内容
        """
        try:
            if subtitle_format.lower() == 'srt':
                return self._generate_srt(segments)
            elif subtitle_format.lower() == 'vtt':
                return self._generate_vtt(segments)
            elif subtitle_format.lower() == 'ass':
                return self._generate_ass(segments)
            else:
                raise ValueError(f"不支持的字幕格式: {subtitle_format}")
        except Exception as e:
            print(f"生成字幕文件失败: {str(e)}")
            return ""
    
    def _generate_srt(self, segments) -> str:
        """
        生成SRT格式字幕
        
        Args:
            segments: Whisper转录的片段列表
            
        Returns:
            str: SRT格式字幕内容
        """
        srt_content = []
        subtitle_index = 1
        
        for segment in segments:
            # 格式化时间戳
            start_time = self._format_timestamp_srt(segment.start)
            end_time = self._format_timestamp_srt(segment.end)
            
            # 添加字幕条目
            srt_content.append(str(subtitle_index))
            srt_content.append(f"{start_time} --> {end_time}")
            srt_content.append(segment.text.strip())
            srt_content.append("")  # 空行分隔
            
            subtitle_index += 1
        
        return "\n".join(srt_content)
    
    def _generate_vtt(self, segments) -> str:
        """
        生成VTT格式字幕
        
        Args:
            segments: Whisper转录的片段列表
            
        Returns:
            str: VTT格式字幕内容
        """
        vtt_content = ["WEBVTT", ""]  # VTT文件头
        
        for segment in segments:
            # 格式化时间戳
            start_time = self._format_timestamp_vtt(segment.start)
            end_time = self._format_timestamp_vtt(segment.end)
            
            # 添加字幕条目
            vtt_content.append(f"{start_time} --> {end_time}")
            vtt_content.append(segment.text.strip())
            vtt_content.append("")  # 空行分隔
        
        return "\n".join(vtt_content)
    
    def _generate_ass(self, segments) -> str:
        """
        生成ASS格式字幕
        
        Args:
            segments: Whisper转录的片段列表
            
        Returns:
            str: ASS格式字幕内容
        """
        # ASS文件头
        ass_header = """[Script Info]
Title: Generated by Video MP3 Tool
ScriptType: v4.00+

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,20,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,2,0,2,10,10,10,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
        
        ass_content = [ass_header]
        
        for segment in segments:
            # 格式化时间戳
            start_time = self._format_timestamp_ass(segment.start)
            end_time = self._format_timestamp_ass(segment.end)
            
            # 添加字幕条目
            dialogue_line = f"Dialogue: 0,{start_time},{end_time},Default,,0,0,0,,{segment.text.strip()}"
            ass_content.append(dialogue_line)
        
        return "\n".join(ass_content)
    
    def _format_timestamp_srt(self, seconds: float) -> str:
        """
        格式化时间戳为SRT格式 (HH:MM:SS,mmm)
        
        Args:
            seconds: 秒数
            
        Returns:
            str: SRT格式时间戳
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        milliseconds = int((seconds % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"
    
    def _format_timestamp_vtt(self, seconds: float) -> str:
        """
        格式化时间戳为VTT格式 (HH:MM:SS.mmm)
        
        Args:
            seconds: 秒数
            
        Returns:
            str: VTT格式时间戳
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        milliseconds = int((seconds % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{milliseconds:03d}"
    
    def _format_timestamp_ass(self, seconds: float) -> str:
        """
        格式化时间戳为ASS格式 (H:MM:SS.cc)
        
        Args:
            seconds: 秒数
            
        Returns:
            str: ASS格式时间戳
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        centiseconds = int((seconds % 1) * 100)
        
        return f"{hours}:{minutes:02d}:{secs:02d}.{centiseconds:02d}"