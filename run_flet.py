#!/usr/bin/env python3

from pathlib import Path
import sys
import flet as ft
import threading

sys.path.append(str(Path(__file__).parent))

# 页面导入
from src.interfaces.base_router import BaseRouter
from src.interfaces.home_page import HomePage
from src.interfaces.generator_page import GeneratorPage
from src.interfaces.localizer_page import LocalizerPage
from src.interfaces.settings_page import SettingsPage

# 控制器导入
from src.controllers.home_controller import HomeController
from src.controllers.generator_controller import GeneratorController
from src.controllers.localizer_controller import LocalizerController

# 服务导入（重要）
from src.service.settings_service import SettingsService

# ============================================================================
# 主入口
# ============================================================================

def main(page: ft.Page):
    """主入口"""
    page.title = "MC Recipe Generator"
    page.window_width = 900
    page.window_height = 700
    
    # 创建共享的SettingsService（关键）
    settings_service = SettingsService()
    settings_service.load_config()  # 初始加载
    
    # 创建路由管理器
    router = BaseRouter(page)
    
    # 创建页面
    pages = {
        "home": HomePage(router, page),
        "generator": GeneratorPage(None, page),
        "localizer": LocalizerPage(None, page),
        "settings": SettingsPage(router, page, settings_service),  # 注入Service
    }
    
    # 注册路由
    route_info = {
        "home": ("首页", ft.icons.HOME),
        "generator": ("生成器", ft.icons.BUILD),
        "localizer": ("本地化", ft.icons.LANGUAGE),
        "settings": ("设置", ft.icons.SETTINGS),
    }
    
    for name, page_obj in pages.items():
        content = page_obj.build()
        router.add_route(name, route_info[name][0], route_info[name][1], lambda c=content: c)
    
    # 初始化其他页面的控制器
    print("🔌 初始化控制器...")
    controllers = {
        "home": HomeController(router, pages["home"]),
        "generator": GeneratorController(pages["generator"]),
        "localizer": LocalizerController(pages["localizer"]),
        # settings不需要Controller
    }
    
    # 手动绑定SettingsPage事件（极简）
    print("🔧 绑定SettingsPage事件...")
    settings_page = pages["settings"]
    
    # 一个按钮一个lambda，直接调用Page的Service方法
    settings_page.register_load_config_event(lambda e: settings_page.load_config())
    settings_page.register_refresh_event(lambda e: settings_page.scan_templates())
    settings_page.register_save_event(lambda e: settings_page.save_config())
    
    # 延迟刷新（避免频繁触发）
    def delayed_refresh(e):
        def run():
            import time
            time.sleep(1.0)
            settings_page.scan_templates()
        threading.Thread(target=run, daemon=True).start()
    
    settings_page.register_template_dir_change(lambda e: delayed_refresh(e))
    
    print("✅ 事件绑定完成")
    
    # 显示首页
    router.go("home")

if __name__ == "__main__":
    ft.app(target=main)