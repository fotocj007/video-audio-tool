#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试字幕生成功能修复
"""

import os
import sys

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from core.speech_to_text import SpeechToText

def test_subtitle_generation_fix():
    """
    测试修复后的字幕生成功能
    """
    print("=== 测试字幕生成功能修复 ===")
    
    # 检查是否有音频文件用于测试
    test_audio_files = [
        "test.mp3",
        "test.wav",
        "sample.mp3",
        "sample.wav"
    ]
    
    audio_file = None
    for file in test_audio_files:
        if os.path.exists(file):
            audio_file = file
            break
    
    if not audio_file:
        print("未找到测试音频文件，请在项目根目录放置以下任一文件：")
        for file in test_audio_files:
            print(f"  - {file}")
        return
    
    print(f"使用音频文件: {audio_file}")
    
    # 测试初始化
    try:
        stt = SpeechToText()
        print("✓ SpeechToText 初始化成功")
    except Exception as e:
        print(f"✗ SpeechToText 初始化失败: {e}")
        return
    
    # 测试字幕生成
    output_file = "test_output.srt"
    
    def progress_callback(progress):
        print(f"进度: {progress}%")
    
    try:
        print("\n开始生成SRT字幕...")
        result = stt.speech_to_subtitle(
            audio_file,
            output_file,
            model_size="tiny",  # 使用最小模型加快测试
            subtitle_format="srt",
            progress_callback=progress_callback
        )
        
        if result['success']:
            print(f"✓ 字幕生成成功: {output_file}")
            print(f"字幕内容预览:")
            if os.path.exists(output_file):
                with open(output_file, 'r', encoding='utf-8') as f:
                    content = f.read()[:500]  # 只显示前500字符
                    print(content)
                    if len(content) == 500:
                        print("...")
        else:
            print(f"✗ 字幕生成失败: {result['error']}")
            
    except Exception as e:
        print(f"✗ 字幕生成异常: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_subtitle_generation_fix()