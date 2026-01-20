
import flet as ft
from pathlib import Path
import sys
from src.interfaces.base_page import BasePage

sys.path.append(str(Path(__file__).parent.parent.parent))

class LocalizerPage(BasePage):
    """本地化页面 - 纯UI"""
    
    def build(self) -> ft.Control:
        # 控制面板
        self.add_component("localize_btn", ft.ElevatedButton("📝 开始本地化", expand=True, width=200))
        self.add_component("open_btn", ft.ElevatedButton("📁 打开输出目录", expand=True, width=200))
        
        # 日志和统计
        self.add_component("log_view", ft.ListView(
            expand=True,
            spacing=5,
            padding=10,
            auto_scroll=True,
        ))
        
        self.add_component("stats_container", ft.Container(
            content=ft.Text("总数: 0 个文件, 0 个条目", size=14, weight=ft.FontWeight.BOLD),
            padding=10,
            bgcolor="#DDDDEE",
            border_radius=5,
        ))
        
        # 布局
        control_panel = ft.Container(
            content=ft.Column([
                ft.Text("📄 本地化工具", size=24, weight=ft.FontWeight.BOLD),
                ft.Row([
                    self.get_component("localize_btn"),
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