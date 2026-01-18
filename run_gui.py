# run_gui.py
import sys
from pathlib import Path

# 将项目根目录加入 Python 路径
sys.path.append(str(Path(__file__).parent))

from src.interfaces.gui import run_gui

if __name__ == "__main__":
    run_gui()