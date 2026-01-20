from pathlib import Path
import sys
import flet as ft

sys.path.append(str(Path(__file__).parent))

from src.interfaces.base_router import BaseRouter
from src.interfaces.home_page import HomePage
from src.interfaces.generator_page import GeneratorPage
from src.interfaces.localizer_page import LocalizerPage
from src.interfaces.settings_page import SettingsPage
from src.service.recipe_service import RecipeService
from src.dao.config_dao import ConfigDAO

# ============================================================================
# 事件处理器工厂（按页面分组）
# ============================================================================

def create_home_handlers(router):
    """首页事件处理器"""
    return {
        "generator_btn": {"click": lambda e: router.go("generator")},
        "localizer_btn": {"click": lambda e: router.go("localizer")},
    }

def create_generator_handlers(page):
    """生成器页面事件处理器"""
    return {
        "dry_run_checkbox": {"change": lambda e: _log_toggle(page, "预览模式", e.control.value)},
        "explain_checkbox": {"change": lambda e: _log_toggle(page, "解释模式", e.control.value)},
        "generate_btn": {"click": lambda e: _handle_generation(page)},
        "open_btn": {"click": lambda e: _open_output_dir(page)},
    }

def create_localizer_handlers(page):
    """本地化页面事件处理器（占位）"""
    return {
        "localize_btn": {"click": lambda e: _show_placeholder(page, "本地化功能开发中")},
        "open_btn": {"click": lambda e: _show_placeholder(page, "打开目录功能待实现")},
    }

def create_settings_handlers(page):
    """设置页面事件处理器"""
    return {
        "save_btn": {"click": lambda e: _save_config(page)},
        "output_dir_field": {"change": lambda e: _log_change("输出目录", e.control.value)},
        "template_dir_field": {"change": lambda e: _log_change("模板目录", e.control.value)},
    }

# ============================================================================
# 辅助函数（处理具体业务逻辑）
# ============================================================================

def _log_toggle(page, name, is_checked):
    """记录复选框切换日志"""
    log_view = page.get_component("log_view")
    if log_view:
        status = "启用" if is_checked else "关闭"
        log_view.controls.append(ft.Text(f"ℹ️ {name}{status}", color="grey", size=12))
        page.page.update()

def _log_change(name, value):
    """记录输入框变更"""
    print(f"📄 {name}: {value}")

def _handle_generation(page):
    """处理生成按钮点击"""
    # 获取所有必需组件
    components = {
        "log_view": page.get_component("log_view"),
        "stats_container": page.get_component("stats_container"),
        "generate_btn": page.get_component("generate_btn"),
        "config_field": page.get_component("config_field"),
        "dry_run_checkbox": page.get_component("dry_run_checkbox"),
        "explain_checkbox": page.get_component("explain_checkbox"),
    }
    
    # 验证组件存在
    missing = [k for k, v in components.items() if not v]
    if missing:
        print(f"❌ 缺少组件: {missing}")
        return
    
    # 1. 初始化UI状态
    _init_generation_ui(components)
    
    # 2. 执行生成
    try:
        _execute_generation(components)
    except Exception as ex:
        _handle_generation_error(components["log_view"], ex)
    finally:
        _restore_generation_ui(components)

def _init_generation_ui(components):
    """初始化生成UI状态"""
    log_view = components["log_view"]
    stats_container = components["stats_container"]
    generate_btn = components["generate_btn"]
    
    log_view.controls.clear()
    stats_container.content = ft.Text("总数: 0 个文件", size=14, weight=ft.FontWeight.BOLD)
    generate_btn.disabled = True
    generate_btn.text = "生成中..."
    generate_btn.update()

def _execute_generation(components):
    """执行核心生成逻辑"""
    config_field = components["config_field"]
    dry_run_checkbox = components["dry_run_checkbox"]
    explain_checkbox = components["explain_checkbox"]
    log_view = components["log_view"]
    stats_container = components["stats_container"]
    
    # 获取参数
    config_path = config_field.value
    dry_run = dry_run_checkbox.value if dry_run_checkbox else True
    explain_mode = explain_checkbox.value if explain_checkbox else False
    
    # 重定向print
    import builtins
    old_print = builtins.print
    
    def custom_print(*args, **kwargs):
        msg = " ".join(str(arg) for arg in args)
        log_view.controls.append(ft.Text(msg, size=12))
        log_view.update()
        old_print(*args, **kwargs)
    
    builtins.print = custom_print
    
    # 创建服务并运行
    service = RecipeService(config_path)
    service.run(dry_run=dry_run, explain_mode=explain_mode)
    
    # 更新统计
    stats = service.output_writer.get_stats()
    stats_container.content = ft.Text(
        f"总数: {stats['total']} 个文件",
        size=14,
        weight=ft.FontWeight.BOLD
    )
    
    # 恢复print
    builtins.print = old_print

def _handle_generation_error(log_view, error):
    """处理生成错误"""
    log_view.controls.append(ft.Text(f"❌ 错误: {error}", color="red", size=14))
    log_view.update()

def _restore_generation_ui(components):
    """恢复生成UI状态"""
    generate_btn = components["generate_btn"]
    generate_btn.disabled = False
    generate_btn.text = "🚀 开始生成"
    generate_btn.update()

def _open_output_dir(page):
    """打开输出目录"""
    log_view = page.get_component("log_view")
    config_field = page.get_component("config_field")
    
    try:
        config = ConfigDAO.load(config_field.value or "config.json")
        output_dir = Path(config.output_dir)
        
        if output_dir.exists():
            import subprocess
            subprocess.Popen(f'explorer "{output_dir.absolute()}"')
            if log_view:
                log_view.controls.append(ft.Text(f"📂 已打开目录", color="orange", size=12))
                page.page.update()
        else:
            if log_view:
                log_view.controls.append(ft.Text("⚠️ 输出目录不存在", color="orange", size=12))
                page.page.update()
    
    except Exception as ex:
        if log_view:
            log_view.controls.append(ft.Text(f"❌ 无法打开目录: {ex}", color="red", size=12))
            page.page.update()

def _show_placeholder(page, message):
    """显示占位功能提示"""
    log_view = page.get_component("log_view")
    if log_view:
        log_view.controls.append(ft.Text(f"🚧 {message}", color="orange", size=14))
        page.page.update()

def _save_config(page):
    """保存配置文件"""
    try:
        config_data = page.get_config()
        Path("config.json").write_text(
            json.dumps(config_data, indent=2, ensure_ascii=False),
            encoding='utf-8'
        )
        
        save_btn = page.get_component("save_btn")
        if save_btn:
            save_btn.text = "✅ 保存成功"
            save_btn.bgcolor = ft.colors.GREEN
            save_btn.update()
            
            # 3秒后恢复
            def restore():
                save_btn.text = "💾 保存配置"
                save_btn.bgcolor = ft.colors.BLUE
                save_btn.update()
            
            page.page.run_task(restore, delay=3)
            
    except Exception as ex:
        print(f"❌ 保存失败: {ex}")

# ============================================================================
# 主入口
# ============================================================================

def main(page: ft.Page):
    """主入口 - 事件驱动架构"""
    page.title = "MC Recipe Generator"
    page.window_width = 900
    page.window_height = 700
    
    # 创建Router
    router = BaseRouter(page)
    
    # 创建并构建所有页面
    pages = {
        "home": HomePage(None, page),
        "generator": GeneratorPage(None, page),
        "localizer": LocalizerPage(None, page),
        "settings": SettingsPage(None, page),
    }
    
    # 构建并注册页面
    for name, page_obj in pages.items():
        content = page_obj.build()
        route_info = {
            "home": ("首页", ft.icons.HOME),
            "generator": ("生成器", ft.icons.BUILD),
            "localizer": ("本地化", ft.icons.LANGUAGE),
            "settings": ("设置", ft.icons.SETTINGS),
        }
        router.add_route(name, route_info[name][0], route_info[name][1], lambda c=content: c)
    
    # 批量绑定事件
    print("🔌 批量绑定事件...")
    for name, page_obj in pages.items():
        handlers = {
            "home": create_home_handlers,
            "generator": create_generator_handlers,
            "localizer": create_localizer_handlers,
            "settings": create_settings_handlers,
        }[name](router if name == "home" else page_obj)
        
        for component_name, events in handlers.items():
            for event_type, handler in events.items():
                page_obj.register_event(component_name, event_type, handler)
        
        page_obj.bind_events()
        print(f"  → {name}: {len(page_obj._event_handlers)} 个事件")
    
    # 显示首页
    router.go("home")

if __name__ == "__main__":
    ft.app(target=main)