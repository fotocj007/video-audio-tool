# -*- coding: utf-8 -*-
"""
简化的配置管理模块
直接使用settings.json文件
"""

import os
import json
from pathlib import Path

def load_settings():
    """加载设置文件"""
    settings_file = Path(__file__).parent / "settings.json"
    try:
        if settings_file.exists():
            with open(settings_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return {}
    except Exception as e:
        print(f"加载配置文件失败: {e}")
        return {}

def save_settings(settings):
    """保存设置文件"""
    settings_file = Path(__file__).parent / "settings.json"
    try:
        with open(settings_file, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"保存配置文件失败: {e}")
        return False

def get_config(key_path, default=None):
    """获取配置值，支持点分隔的路径"""
    settings = load_settings()
    keys = key_path.split('.')
    value = settings
    try:
        for key in keys:
            value = value[key]
        return value
    except (KeyError, TypeError):
        return default

def is_feature_enabled(feature_name):
    """检查功能是否启用"""
    return get_config(f'features.{feature_name}', True)

def get_window_geometry():
    """获取窗口几何信息"""
    size = get_config('app.window_size', [1200, 800])
    position = get_config('app.window_position', [100, 100])
    return {
        'width': size[0],
        'height': size[1],
        'x': position[0],
        'y': position[1]
    }

def set_window_geometry(width, height, x, y):
    """设置窗口几何信息"""
    settings = load_settings()
    if 'app' not in settings:
        settings['app'] = {}
    settings['app']['window_size'] = [width, height]
    settings['app']['window_position'] = [x, y]
    save_settings(settings)