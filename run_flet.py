
from pathlib import Path
import sys
import flet as ft

# 添加项目根目录到sys.path
sys.path.append(str(Path(__file__).parent))

from src.interfaces.base_router import BaseRouter
from src.interfaces.home_page import HomePage
from src.interfaces.generator_page import GeneratorPage
from src.interfaces.localizer_page import LocalizerPage
from src.interfaces.settings_page import SettingsPage

# 控制器导入
from src.controllers.home_controller import HomeController
from src.controllers.generator_controller import GeneratorController
from src.controllers.localizer_controller import LocalizerController
from src.controllers.settings_controller import SettingsController

# ============================================================================
# 主入口
# ============================================================================

def main(page: ft.Page):
    """主入口 - 控制器模式"""
    page.title = "MC Recipe Generator"
    page.window_width = 900
    page.window_height = 700
    
    # 1. 创建路由
    router = BaseRouter(page)
    
    # 2. 创建页面实例
    pages = {
        "home": HomePage(router, page),
        "generator": GeneratorPage(None, page),
        "localizer": LocalizerPage(None, page),
        "settings": SettingsPage(router, page),
    }
    
    # 3. 注册路由和构建内容
    route_info = {
        "home": ("首页", ft.icons.HOME),
        "generator": ("生成器", ft.icons.BUILD),
        "localizer": ("本地化", ft.icons.LANGUAGE),
        "settings": ("设置", ft.icons.SETTINGS),
    }
    
    for name, page_obj in pages.items():
        content = page_obj.build()
        router.add_route(name, route_info[name][0], route_info[name][1], lambda c=content: c)
    
    # 4. 创建并初始化控制器（关键！）
    print("🔌 初始化控制器...")
    controllers = {
        "home": HomeController(router, pages["home"]),
        "generator": GeneratorController(pages["generator"]),
        "localizer": LocalizerController(pages["localizer"]),
        "settings": SettingsController(pages["settings"]),
    }
    
    # 5. 显示首页
    router.go("home")

if __name__ == "__main__":
    ft.app(target=main)