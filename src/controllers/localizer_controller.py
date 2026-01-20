
import flet as ft

class LocalizerController:
    """本地化控制器（占位实现）"""
    
    def __init__(self, page):
        self.page = page
        self._bind_events()
    
    def _bind_events(self):
        """绑定事件"""
        localize_btn = self.page.get_component("localize_btn")
        if localize_btn:
            localize_btn.on_click = lambda e: self._show_placeholder("本地化功能开发中")
        
        open_btn = self.page.get_component("open_btn")
        if open_btn:
            open_btn.on_click = lambda e: self._show_placeholder("打开目录功能待实现")
    
    def _show_placeholder(self, message: str):
        """显示占位提示"""
        log_view = self.page.get_component("log_view")
        if log_view:
            log_view.controls.append(ft.Text(f"🚧 {message}", color="orange", size=14))
            log_view.update()