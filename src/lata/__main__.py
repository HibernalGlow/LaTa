#!/usr/bin/env python3
"""
Taskfile 启动器核心模块
"""

import os
import sys
import subprocess
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any

from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel

console = Console()

class TaskfileLauncher:
    def __init__(self, taskfile_path: Path = None):
        self.taskfile_path = taskfile_path or self._find_taskfile()
        self.tasks = {}
        self._load_taskfile()
    
    def _find_taskfile(self) -> Path:
        """查找 Taskfile.yml - 优先使用脚本同目录下的，然后是当前工作目录"""
        # 首先尝试脚本同目录下的 Taskfile.yml
        script_dir = Path(__file__).parent
        script_taskfile = script_dir / "Taskfile.yml"
        
        if script_taskfile.exists():
            return script_taskfile
        else:
            # 如果脚本目录没有，则使用当前工作目录
            return Path("Taskfile.yml")
    
    def _load_taskfile(self):
        """加载 Taskfile.yml 并解析任务"""
        try:
            with open(self.taskfile_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            self.tasks = data.get('tasks', {})
            
        except Exception as e:
            console.print(f"[red]加载 Taskfile 失败: {e}[/red]")
            sys.exit(1)
    
    def _display_tasks(self):
        """显示所有可用任务"""
        console.print(Panel.fit(
            "[bold blue]Taskfile 任务选择器[/bold blue]",
            border_style="blue"
        ))
        
        try:
            # 直接使用 task --list 显示任务列表
            result = subprocess.run(
                ['task', '--taskfile', str(self.taskfile_path), '--list'],
                cwd=self.taskfile_path.parent,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            
            if result.returncode == 0:
                console.print(result.stdout)
            else:
                console.print(f"[red]获取任务列表失败: {result.stderr}[/red]")
                
        except Exception as e:
            console.print(f"[red]执行 task --list 失败: {e}[/red]")
    
    def _select_task(self) -> Optional[str]:
        """交互式选择任务"""
        self._display_tasks()
        
        task_names = [name for name in self.tasks.keys() if name != 'default']
        
        while True:
            console.print("\n[yellow]请选择要执行的任务:[/yellow]")
            
            # 显示任务选项
            for i, task_name in enumerate(task_names, 1):
                console.print(f"  [cyan]{i}[/cyan]. {task_name}")
            
            console.print(f"  [cyan]0[/cyan]. 退出")
            
            choice = Prompt.ask(
                "[bold green]请输入选项编号[/bold green]",
                choices=[str(i) for i in range(len(task_names) + 1)],
                default="0"
            )
            
            if choice == "0":
                return None
            
            return task_names[int(choice) - 1]
    
    def _get_task_input(self, task_name: str) -> Optional[str]:
        """获取任务所需的输入参数"""
        task_info = self.tasks.get(task_name, {})
        prompt_text = task_info.get('prompt')
        
        if not prompt_text:
            return ""
        
        # 特殊处理不同类型的提示
        if "y/N" in prompt_text:
            # 是/否选择
            return "y" if Confirm.ask(f"[yellow]{prompt_text}[/yellow]", default=False) else "n"
        else:
            # 文本输入
            return Prompt.ask(f"[yellow]{prompt_text}[/yellow]")
    
    def _run_task(self, task_name: str, user_input: str = "") -> int:
        """执行指定的任务"""
        try:
            console.print(f"[blue]执行任务: {task_name}[/blue]")
            
            # 构建命令
            cmd = ['task', '--taskfile', str(self.taskfile_path), task_name]
            
            # 如果有用户输入，添加到命令中
            if user_input:
                cmd.append(user_input)
            
            # 执行命令
            result = subprocess.run(
                cmd,
                cwd=self.taskfile_path.parent,
                env=dict(os.environ, CLI_ARGS=user_input)
            )
            
            return result.returncode
            
        except KeyboardInterrupt:
            console.print("\n[yellow]任务被用户中断[/yellow]")
            return 0
        except Exception as e:
            console.print(f"[red]执行任务时出错: {e}[/red]")
            return 1
    
    def run(self) -> int:
        """运行交互式任务选择器"""
        if not self.taskfile_path.exists():
            console.print(f"[red]错误: Taskfile 不存在: {self.taskfile_path}[/red]")
            return 1
        
        while True:
            task_name = self._select_task()
            
            if task_name is None:
                console.print("[yellow]退出任务选择器[/yellow]")
                return 0
            
            # 获取任务输入
            user_input = self._get_task_input(task_name)
            
            # 执行任务
            result = self._run_task(task_name, user_input)
            
            if result != 0:
                console.print(f"[red]任务 '{task_name}' 执行失败 (退出码: {result})[/red]")
            else:
                console.print(f"[green]任务 '{task_name}' 执行成功[/green]")
            
            # 询问是否继续
            if not Confirm.ask("\n[yellow]是否继续选择其他任务?[/yellow]", default=True):
                break
        
        return 0

def launch(taskfile_path: Path = None) -> int:
    """启动 Taskfile 选择器的便捷函数"""
    launcher = TaskfileLauncher(taskfile_path)
    return launcher.run()

def main():
    # 支持命令行参数指定 Taskfile 路径
    if len(sys.argv) > 1:
        taskfile_path = Path(sys.argv[1])
        sys.exit(launch(taskfile_path))
    else:
        sys.exit(launch())
        
if __name__ == "__main__":
    main()