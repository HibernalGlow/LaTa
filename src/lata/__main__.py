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
        """查找 Taskfile.yml - 按优先级搜索多个位置"""
        # 搜索优先级：
        # 1. 调用脚本的目录（如果是通过外部脚本调用）
        # 2. 当前工作目录
        # 3. 当前目录的父目录（递归向上查找）
        # 4. 用户主目录
        # 5. 包内示例文件（仅作为最后的备选）

        search_paths = []

        # 1. 检查是否有调用脚本的目录信息
        # 通过环境变量传递调用脚本的目录
        caller_script_dir = os.environ.get('LATA_CALLER_DIR')
        if caller_script_dir:
            caller_dir = Path(caller_script_dir)
            caller_taskfile = caller_dir / "Taskfile.yml"
            search_paths.append(caller_taskfile)

        # 2. 当前工作目录及其父目录
        current_dir = Path.cwd()
        for parent in [current_dir] + list(current_dir.parents):
            taskfile_path = parent / "Taskfile.yml"
            search_paths.append(taskfile_path)
            # 只向上查找 5 层，避免搜索过深
            if len(search_paths) >= 6:  # 调整为6，因为可能有caller_dir
                break

        # 3. 用户主目录
        home_taskfile = Path.home() / "Taskfile.yml"
        search_paths.append(home_taskfile)

        # 4. 包内示例文件（最后备选）
        script_dir = Path(__file__).parent
        package_taskfile = script_dir / "Taskfile.yml"
        search_paths.append(package_taskfile)

        # 查找第一个存在的文件
        for taskfile_path in search_paths:
            if taskfile_path.exists():
                return taskfile_path

        # 如果都不存在，返回调用脚本目录或当前目录的 Taskfile.yml
        if caller_script_dir:
            return Path(caller_script_dir) / "Taskfile.yml"
        return Path("Taskfile.yml")

    def show_search_info(self):
        """显示 Taskfile 搜索信息"""
        console.print("\n[blue]Taskfile.yml 搜索路径信息:[/blue]")

        search_index = 1

        # 调用脚本目录
        caller_script_dir = os.environ.get('LATA_CALLER_DIR')
        if caller_script_dir:
            caller_dir = Path(caller_script_dir)
            caller_taskfile = caller_dir / "Taskfile.yml"
            exists = "[green]YES[/green]" if caller_taskfile.exists() else "[red]NO[/red]"
            console.print(f"  {search_index}. {exists} {caller_taskfile} (调用脚本目录)")
            search_index += 1

        # 当前工作目录及父目录
        current_dir = Path.cwd()
        console.print(f"[cyan]当前工作目录: {current_dir}[/cyan]")

        search_paths = []
        for parent in [current_dir] + list(current_dir.parents):
            taskfile_path = parent / "Taskfile.yml"
            exists = "[green]YES[/green]" if taskfile_path.exists() else "[red]NO[/red]"
            console.print(f"  {search_index}. {exists} {taskfile_path}")
            search_paths.append(taskfile_path)
            search_index += 1
            if len(search_paths) >= 5:
                break

        # 用户主目录
        home_taskfile = Path.home() / "Taskfile.yml"
        exists = "[green]YES[/green]" if home_taskfile.exists() else "[red]NO[/red]"
        console.print(f"  {search_index}. {exists} {home_taskfile} (用户主目录)")
        search_index += 1

        # 包内示例
        script_dir = Path(__file__).parent
        package_taskfile = script_dir / "Taskfile.yml"
        exists = "[green]YES[/green]" if package_taskfile.exists() else "[red]NO[/red]"
        console.print(f"  {search_index}. {exists} {package_taskfile} (包内示例)")

        console.print(f"\n[yellow]当前使用: {self.taskfile_path.absolute()}[/yellow]")
    
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
            try:
                console.print("\n[yellow]请选择要执行的任务:[/yellow]")

                # 显示任务选项
                for i, task_name in enumerate(task_names, 1):
                    console.print(f"  [cyan]{i}[/cyan]. {task_name}")

                console.print(f"  [cyan]0[/cyan]. 退出")
                console.print("[dim]提示: 按 Ctrl+C 可随时安全退出[/dim]")

                choice = Prompt.ask(
                    "[bold green]请输入选项编号[/bold green]",
                    choices=[str(i) for i in range(len(task_names) + 1)],
                    default="1"
                )

                if choice == "0":
                    return None

                return task_names[int(choice) - 1]

            except KeyboardInterrupt:
                console.print("\n[yellow]检测到 Ctrl+C，正在安全退出...[/yellow]")
                return None
            except EOFError:
                console.print("\n[yellow]检测到输入结束，正在退出...[/yellow]")
                return None
    
    def _get_task_input(self, task_name: str) -> Optional[str]:
        """获取任务所需的输入参数"""
        task_info = self.tasks.get(task_name, {})
        prompt_text = task_info.get('prompt')

        if not prompt_text:
            return ""

        try:
            # 特殊处理不同类型的提示
            if "y/N" in prompt_text:
                # 是/否选择
                return "y" if Confirm.ask(f"[yellow]{prompt_text}[/yellow]", default=False) else "n"
            else:
                # 文本输入
                return Prompt.ask(f"[yellow]{prompt_text}[/yellow]")
        except KeyboardInterrupt:
            console.print("\n[yellow]输入被中断，跳过此任务[/yellow]")
            return None
        except EOFError:
            console.print("\n[yellow]输入结束，跳过此任务[/yellow]")
            return None
    
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
            console.print("\n[yellow]提示: Taskfile.yml 搜索路径优先级:[/yellow]")
            console.print("  1. 当前工作目录及其父目录")
            console.print("  2. 用户主目录")
            console.print("  3. 包内示例文件")
            console.print(f"\n[cyan]当前工作目录: {Path.cwd()}[/cyan]")
            console.print(f"[cyan]期望的 Taskfile 位置: {self.taskfile_path.absolute()}[/cyan]")
            return 1

        try:
            while True:
                task_name = self._select_task()

                if task_name is None:
                    console.print("[yellow]退出任务选择器[/yellow]")
                    return 0

                # 获取任务输入
                user_input = self._get_task_input(task_name)

                # 如果用户在输入阶段按了 Ctrl+C，跳过此任务
                if user_input is None:
                    continue

                # 执行任务
                result = self._run_task(task_name, user_input)

                if result != 0:
                    console.print(f"[red]任务 '{task_name}' 执行失败 (退出码: {result})[/red]")
                else:
                    console.print(f"[green]任务 '{task_name}' 执行成功[/green]")

                # 询问是否继续
                try:
                    if not Confirm.ask("\n[yellow]是否继续选择其他任务?[/yellow]", default=True):
                        break
                except KeyboardInterrupt:
                    console.print("\n[yellow]检测到 Ctrl+C，正在安全退出...[/yellow]")
                    break
                except EOFError:
                    console.print("\n[yellow]检测到输入结束，正在退出...[/yellow]")
                    break

        except KeyboardInterrupt:
            console.print("\n[yellow]程序被用户中断，正在安全退出...[/yellow]")
            return 0
        except Exception as e:
            console.print(f"[red]程序运行时出现错误: {e}[/red]")
            return 1

        return 0

def launch(taskfile_path: Path = None) -> int:
    """启动 Taskfile 选择器的便捷函数"""
    launcher = TaskfileLauncher(taskfile_path)
    return launcher.run()

def main():
    """主入口函数"""
    try:
        # 处理命令行参数
        if len(sys.argv) > 1:
            arg = sys.argv[1]

            # 显示搜索信息
            if arg in ["-i", "--info", "--search-info"]:
                launcher = TaskfileLauncher()
                launcher.show_search_info()
                sys.exit(0)

            # 显示帮助
            elif arg in ["-h", "--help"]:
                console.print("[bold blue]LaTa - Taskfile 启动器[/bold blue]")
                console.print("\n[yellow]用法:[/yellow]")
                console.print("  lata                    # 启动交互式任务选择器")
                console.print("  lata <taskfile_path>    # 使用指定的 Taskfile")
                console.print("  lata -i, --info         # 显示 Taskfile 搜索路径信息")
                console.print("  lata -h, --help         # 显示此帮助信息")
                console.print("\n[yellow]Taskfile 搜索优先级:[/yellow]")
                console.print("  1. 当前工作目录及其父目录（向上最多 5 层）")
                console.print("  2. 用户主目录")
                console.print("  3. 包内示例文件")
                sys.exit(0)

            # 指定 Taskfile 路径
            else:
                taskfile_path = Path(arg)
                sys.exit(launch(taskfile_path))
        else:
            sys.exit(launch())
    except KeyboardInterrupt:
        console.print("\n[yellow]程序被用户中断，已安全退出[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[red]程序启动失败: {e}[/red]")
        sys.exit(1)
        
if __name__ == "__main__":
    main()