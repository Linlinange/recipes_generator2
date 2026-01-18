# main.py
from src import RecipeGenerator
from src.interfaces.gui import run_gui
import argparse

def main():
    parser = argparse.ArgumentParser(
        description="MC Recipe Generator - 多界面支持",
        epilog="示例: python main.py --ui tui 或 python main.py --ui gui"
    )
    
    parser.add_argument(
        "--ui", 
        choices=["cli", "gui"], 
        default="cli", 
        help="界面模式: cli(命令行) 或 gui(图形界面)"
    )
    
    parser.add_argument("--dry-run", action="store_true", help="预览模式")
    parser.add_argument("--explain", action="store_true", help="解释模式")
    
    args = parser.parse_args()
    
    if args.ui == "gui":
        # 启动 Streamlit GUI
        run_gui()
    else:
        # 启动 CLI 模式
        generator = RecipeGenerator("config.json")
        generator.run(dry_run=args.dry_run, explain_mode=args.explain)

if __name__ == "__main__":
    main()