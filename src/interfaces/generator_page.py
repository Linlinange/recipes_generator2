
import flet as ft
import sys
from pathlib import Path
from src.interfaces.base_page import BasePage

sys.path.append(str(Path(__file__).parent.parent.parent))

class GeneratorPage(BasePage):
    """生成器页面 - 纯UI"""
    
    def build(self) -> ft.Control:
        # 控制面板组件
        self.add_component("dry_run_checkbox", ft.Checkbox(label="预览模式", value=True))
        self.add_component("explain_checkbox", ft.Checkbox(label="解释模式", value=False))
        self.add_component("generate_btn", ft.ElevatedButton("🚀 开始生成", expand=True, width=200))
        self.add_component("open_btn", ft.ElevatedButton("📁 打开输出目录", expand=True, width=200))
        
        # 日志和统计区域
        self.add_component("log_view", ft.ListView(
            expand=True,
            spacing=5,
            padding=10,
            auto_scroll=True,
        ))
        
        self.add_component("stats_container", ft.Container(
            content=ft.Text("总数: 0 个文件", size=14, weight=ft.FontWeight.BOLD),
            padding=10,
            bgcolor="#DDDDEE",
            border_radius=5,
        ))
        
        # 布局组装
        control_panel = ft.Container(
            content=ft.Column([
                ft.Text("⚙️ 配方生成器", size=24, weight=ft.FontWeight.BOLD),
                ft.Row([
                    self.get_component("dry_run_checkbox"),
                    self.get_component("explain_checkbox"),
                ], spacing=20),
                ft.Row([
                    self.get_component("generate_btn"),
                    self.get_component("open_btn"),
                ], spacing=10),
            ], spacing=15),
            padding=20,
            bgcolor="#DDDDEE",
            height=220,
        )
        
        return ft.Column([
            control_panel,
            self.get_component("log_view"),
            self.get_component("stats_container"),
        ], expand=True, spacing=10)