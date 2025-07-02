#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多媒体处理工具启动脚本
用于检查依赖并启动应用程序
"""

import sys
import os
import subprocess
from pathlib import Path

def check_dependencies():
    """检查必要的依赖是否已安装"""
    required_packages = [
        'PySide6',
        'moviepy', 
        'whisper',
        'pydub',
        'TTS',
        'torch'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package} 已安装")
        except ImportError:
            missing_packages.append(package)
            print(f"✗ {package} 未安装")
    
    return missing_packages

def check_ffmpeg():
    """检查FFmpeg是否可用"""
    try:
        # 检查当前目录下的ffmpeg.exe
        current_dir = Path(__file__).parent
        ffmpeg_path = current_dir / "ffmpeg.exe"
        
        if ffmpeg_path.exists():
            print("✓ FFmpeg 在当前目录中找到")
            # 将当前目录添加到PATH
            os.environ['PATH'] = str(current_dir) + os.pathsep + os.environ.get('PATH', '')
            return True
        
        # 检查系统PATH中的ffmpeg
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✓ FFmpeg 在系统PATH中找到")
            return True
        else:
            print("✗ FFmpeg 未找到")
            return False
            
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
        print("✗ FFmpeg 未找到")
        return False

def install_missing_packages(packages):
    """安装缺失的包"""
    if not packages:
        return True
        
    print(f"\n需要安装以下包: {', '.join(packages)}")
    response = input("是否现在安装? (y/n): ")
    
    if response.lower() in ['y', 'yes', '是']:
        try:
            # 特殊处理torch安装
            if 'torch' in packages:
                print("正在安装PyTorch...")
                subprocess.check_call([
                    sys.executable, '-m', 'pip', 'install', 
                    'torch', 'torchaudio', 
                    '--index-url', 'https://download.pytorch.org/whl/cu118'
                ])
                packages.remove('torch')
            
            # 安装其他包
            if packages:
                print(f"正在安装其他依赖: {', '.join(packages)}")
                subprocess.check_call([
                    sys.executable, '-m', 'pip', 'install'
                ] + packages)
            
            print("\n所有依赖安装完成！")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"\n安装失败: {e}")
            return False
    else:
        print("\n请手动安装缺失的依赖后再运行程序。")
        return False

def test_imports():
    """测试关键模块导入"""
    print("\n测试模块导入...")
    
    # 测试PySide6
    try:
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import Qt
        from PySide6.QtGui import QAction
        print("✓ PySide6导入成功")
    except ImportError as e:
        print(f"✗ PySide6导入失败: {e}")
        return False
    
    # 测试核心模块
    try:
        from core.video_handler import VideoHandler
        from core.audio_handler import AudioHandler
        print("✓ 核心模块导入成功")
    except ImportError as e:
        print(f"✗ 核心模块导入失败: {e}")
        return False
    
    # 测试GUI模块
    try:
        from gui.main_window import MainWindow
        print("✓ GUI模块导入成功")
    except ImportError as e:
        print(f"✗ GUI模块导入失败: {e}")
        print(f"详细错误: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def main():
    """主函数"""
    print("多媒体处理工具 - 启动检查")
    print("=" * 40)
    
    # 检查Python版本
    if sys.version_info < (3, 8):
        print("错误: 需要Python 3.8或更高版本")
        sys.exit(1)
    
    print(f"✓ Python版本: {sys.version.split()[0]}")
    
    # 检查依赖
    print("\n检查Python依赖...")
    missing_packages = check_dependencies()
    
    if missing_packages:
        if not install_missing_packages(missing_packages):
            sys.exit(1)
    
    # 测试导入
    if not test_imports():
        print("\n模块导入测试失败，请检查安装。")
        input("按回车键退出...")
        sys.exit(1)
    
    # 检查FFmpeg
    print("\n检查FFmpeg...")
    if not check_ffmpeg():
        print("\n警告: FFmpeg未找到。某些功能可能无法正常工作。")
        print("请确保ffmpeg.exe在当前目录中，或已添加到系统PATH中。")
        
        response = input("是否继续启动程序? (y/n): ")
        if response.lower() not in ['y', 'yes', '是']:
            sys.exit(1)
    
    # 启动应用程序
    print("\n" + "=" * 40)
    print("启动多媒体处理工具...")
    
    try:
        from main import main as app_main
        app_main()
    except Exception as e:
        print(f"启动失败: {e}")
        import traceback
        traceback.print_exc()
        input("按回车键退出...")
        sys.exit(1)

if __name__ == "__main__":
    main()