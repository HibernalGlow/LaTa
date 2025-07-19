#!/usr/bin/env python3
"""
Taskfile Launcher 使用示例
"""

def example_1():
    """示例1: 最简单的一键启动"""
    print("=== 示例1: 一键启动 ===")
    import lata
    lata.start()

def example_2():
    """示例2: 使用启动函数"""
    print("=== 示例2: 使用启动函数 ===")
    from lata import launch
    launch()

def example_3():
    """示例3: 使用类实例"""
    print("=== 示例3: 使用类实例 ===")
    from lata import TaskfileLauncher
    
    # 使用默认查找逻辑
    launcher = TaskfileLauncher()
    launcher.run()

def example_4():
    """示例4: 指定自定义 Taskfile 路径"""
    print("=== 示例4: 指定自定义路径 ===")
    from lata import TaskfileLauncher
    from pathlib import Path
    
    # 指定 Taskfile 路径
    custom_path = Path("src/autorepack/config/Taskfile.yml")
    if custom_path.exists():
        launcher = TaskfileLauncher(custom_path)
        launcher.run()
    else:
        print(f"Taskfile 不存在: {custom_path}")

if __name__ == "__main__":
    print("Taskfile Launcher 使用示例")
    print("选择要运行的示例:")
    print("1. 一键启动")
    print("2. 使用启动函数")
    print("3. 使用类实例")
    print("4. 指定自定义路径")
    
    choice = input("请输入选项 (1-4): ").strip()
    
    if choice == "1":
        example_1()
    elif choice == "2":
        example_2()
    elif choice == "3":
        example_3()
    elif choice == "4":
        example_4()
    else:
        print("无效选项，使用默认示例")
        example_1()
