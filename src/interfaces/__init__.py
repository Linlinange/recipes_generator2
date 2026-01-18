"""
用户界面模块

提供多种交互方式：
- CLI: 命令行模式（默认）
- GUI: Streamlit 图形界面
- TUI: Textual 终端界面（可选）
"""

from .gui import run_gui

__all__ = ["run_gui"]