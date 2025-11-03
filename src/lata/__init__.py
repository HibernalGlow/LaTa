#!/usr/bin/env python3
"""
Taskfile 启动器包
提供简单的一键导入启动功能
"""

__version__ = "0.1.2"

# 延迟导入以避免循环导入问题
def get_launcher():
    """获取 TaskfileLauncher 类"""
    from .__main__ import TaskfileLauncher
    return TaskfileLauncher

def launch(taskfile_path=None):
    """启动 Taskfile 选择器"""
    from .__main__ import launch as _launch
    return _launch(taskfile_path)

def start():
    """一键启动 Taskfile 选择器"""
    return launch()

__all__ = ["get_launcher", "launch", "start"]
