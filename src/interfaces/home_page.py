
import flet as ft
from src.interfaces.base_page import BasePage

class HomePage(BasePage):
    """首页 - 纯UI"""
    
    def build(self) -> ft.Control:
        # 创建组件
        self.add_component(
            "welcome_text",
            ft.Text("🏠 MC Recipe Generator", size=30, weight=ft.FontWeight.BOLD)
        )
        
        self.add_component(
            "generator_btn",
            ft.ElevatedButton("开始生成配方 →", width=200, height=50)
        )
        
        self.add_component(
            "localizer_btn",
            ft.ElevatedButton("开始批量本地化 →", width=200, height=50)
        )
        
        # 组装页面
        return ft.Container(
            content=ft.Column([
                self.get_component("welcome_text"),
                ft.Text("欢迎使用Minecraft配方生成工具！", size=16),
                ft.Text("功能特色：", size=18, weight=ft.FontWeight.BOLD),
                ft.Text("• 支持批量生成JSON配方文件"),
                ft.Text("• 灵活的模板占位符替换"),
                ft.Text("• 预览模式避免误操作"),
                ft.Text("• 可视化日志输出"),
                ft.Divider(),
                self.get_component("generator_btn"),
                self.get_component("localizer_btn"),
            ], expand=True, spacing=20),
            padding=ft.padding.only(top=20)
        )