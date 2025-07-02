#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多媒体处理工具主程序
基于PySide6的桌面应用程序，提供视频和音频处理功能
"""

import sys
import os
import traceback
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def check_and_import():
    """检查并导入必要模块"""
    try:
        print("正在导入PySide6...")
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import Qt
        print("✓ PySide6基础模块导入成功")
        
        print("正在导入GUI模块...")
        from gui.main_window import MainWindow
        print("✓ GUI模块导入成功")
        
        return QApplication, Qt, MainWindow
        
    except ImportError as e:
        print(f"\n导入错误: {e}")
        print("\n可能的解决方案:")
        print("1. 安装依赖: pip install -r requirements.txt")
        print("2. 检查PySide6版本: pip install PySide6>=6.0.0")
        print("3. 重新安装PySide6: pip uninstall PySide6 && pip install PySide6")
        
        print("\n详细错误信息:")
        traceback.print_exc()
        return None, None, None
    except Exception as e:
        print(f"\n未知错误: {e}")
        traceback.print_exc()
        return None, None, None

def main():
    """主函数"""
    print("多媒体处理工具启动中...")
    
    # 检查并导入模块
    QApplication, Qt, MainWindow = check_and_import()
    
    if not all([QApplication, Qt, MainWindow]):
        print("\n模块导入失败，程序无法启动。")
        input("按回车键退出...")
        sys.exit(1)
    
    try:
        print("正在初始化应用程序...")
        
        # 创建应用程序实例（PySide6会自动处理高DPI）
        app = QApplication(sys.argv)
        app.setApplicationName("多媒体处理工具")
        app.setApplicationVersion("1.0")
        app.setOrganizationName("VMTool")
        
        print("正在创建主窗口...")
        # 创建并显示主窗口
        window = MainWindow()
        print("主窗口创建完成，正在显示...")
        window.show()
        
        print("应用程序启动成功！")
        
        # 运行应用程序
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"\n应用程序启动失败: {e}")
        traceback.print_exc()
        input("按回车键退出...")
        sys.exit(1)

if __name__ == "__main__":
    main()