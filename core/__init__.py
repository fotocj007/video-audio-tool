#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VMTool 核心视频处理模块

模块化视频处理工具包，提供以下功能：
- 视频拆分 (VideoSplitter)
- 音频提取 (AudioExtractor) 
- 视频音频合并 (VideoAudioMerger)
- 统一接口 (UnifiedVideoHandler)
- 向后兼容 (VideoHandler)
"""

__version__ = "2.0.0"
__author__ = "VMTool Team"

# 可选导入，避免在依赖未安装时程序崩溃
try:
    from .video_handler import VideoHandler
    from .unified_video_handler import UnifiedVideoHandler
    from .base_handler import BaseVideoHandler
    from .video_splitter import VideoSplitter
    from .audio_extractor import AudioExtractor
    from .video_audio_merger import VideoAudioMerger
    VIDEO_HANDLER_AVAILABLE = True
except ImportError as e:
    print(f"警告: 视频处理模块导入失败: {e}")
    VideoHandler = None
    UnifiedVideoHandler = None
    BaseVideoHandler = None
    VideoSplitter = None
    AudioExtractor = None
    VideoAudioMerger = None
    VIDEO_HANDLER_AVAILABLE = False

# 保持向后兼容
try:
    from .audio_handler import AudioHandler
    AUDIO_HANDLER_AVAILABLE = True
except ImportError as e:
    print(f"注意: 旧版音频处理模块不存在: {e}")
    AudioHandler = None
    AUDIO_HANDLER_AVAILABLE = False

# 导出的公共接口
__all__ = [
    'VideoHandler',           # 向后兼容的主接口
    'UnifiedVideoHandler',    # 新的统一接口
    'BaseVideoHandler',       # 基础处理器
    'VideoSplitter',          # 视频拆分器
    'AudioExtractor',         # 音频提取器
    'VideoAudioMerger',       # 视频音频合并器
    'AudioHandler',           # 旧版音频处理器（如果存在）
    'VIDEO_HANDLER_AVAILABLE',
    'AUDIO_HANDLER_AVAILABLE'
]

# 便捷函数
def create_video_handler():
    """创建默认的视频处理器实例"""
    if VIDEO_HANDLER_AVAILABLE:
        return VideoHandler()
    else:
        raise ImportError("视频处理模块不可用")

def create_unified_handler():
    """创建统一视频处理器实例"""
    if VIDEO_HANDLER_AVAILABLE:
        return UnifiedVideoHandler()
    else:
        raise ImportError("统一视频处理器不可用")

def get_version():
    """获取版本信息"""
    return __version__

def get_supported_formats():
    """获取支持的格式信息"""
    if VIDEO_HANDLER_AVAILABLE:
        handler = UnifiedVideoHandler()
        return handler.get_supported_formats()
    else:
        return {"error": "视频处理模块不可用"}