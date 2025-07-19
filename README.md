# Taskfile Launcher

一个简单易用的 Taskfile 启动器包，提供交互式任务选择界面。

## 功能特点

- 🚀 一键导入启动
- 🎨 Rich 彩色界面
- 📝 编号选择任务
- 🔍 自动查找 Taskfile.yml
- ⚙️ 支持任务参数输入

## 安装

将 `taskfile_launcher` 目录复制到你的项目中，或者添加到 Python 路径。

## 使用方法

### 1. 一键启动（推荐）

```python
import taskfile_launcher
taskfile_launcher.start()
```

### 2. 使用启动函数

```python
from taskfile_launcher import launch
launch()
```

### 3. 使用类实例

```python
from taskfile_launcher import TaskfileLauncher

# 使用默认查找逻辑
launcher = TaskfileLauncher()
launcher.run()

# 指定 Taskfile 路径
from pathlib import Path
launcher = TaskfileLauncher(Path("custom/Taskfile.yml"))
launcher.run()
```

### 4. 命令行使用

```bash
python -m taskfile_launcher.launcher
python -m taskfile_launcher.launcher /path/to/Taskfile.yml
```

## Taskfile 查找逻辑

1. 优先使用包目录下的 `Taskfile.yml`
2. 如果不存在，则查找当前工作目录的 `Taskfile.yml`
3. 可以手动指定 Taskfile 路径

## 示例 Taskfile.yml

包中包含了一个示例 `Taskfile.yml`，包含以下任务：

- `image`: 图片处理模式
- `gallery`: 画集处理模式  
- `pack-only`: 仅打包模式
- `test`: 测试任务

## 依赖

- `rich`: 用于彩色终端界面
- `pyyaml`: 用于解析 Taskfile.yml
- `task`: Taskfile 执行器（需要单独安装）

## 许可证

MIT License
