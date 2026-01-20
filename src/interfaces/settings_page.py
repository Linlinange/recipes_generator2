import flet as ft
import threading
from pathlib import Path
from typing import Optional, List, Dict
from src.interfaces.base_page import BasePage
from src.service.settings_service import SettingsService


class SettingsPage(BasePage):
    """
    SettingsPage - UI层，调用SettingsService
    职责：UI展示、事件转发、UI状态更新
    """
    
    def __init__(self, router, page: ft.Page, service: SettingsService):
        super().__init__(router, page)
        # 持有Service引用
        self.service = service
        
        # UI状态
        self._template_checkboxes: Dict[str, ft.Checkbox] = {}
        self._selected_count_text: ft.Text = ft.Text("已选择: 0 个模板", size=14)
        self._status_text: ft.Text = ft.Text("", size=12, color=ft.colors.ORANGE)
        self._refresh_btn: Optional[ft.ElevatedButton] = None
        self._save_btn: Optional[ft.ElevatedButton] = None
    
    def build(self) -> ft.Control:
        """构建UI（代码与之前基本相同）"""
        # ... build代码保持不变 ...
    
    # ==================== 业务方法（调用Service） ====================
    
    def load_config(self, config_path: str = None) -> bool:
        """加载配置（供run_flet调用）"""
        success = self.service.load_config(config_path)
        
        if success:
            self._update_ui_from_service()
            self.scan_templates()
            self.show_status_message("✅ 配置加载成功", is_error=False)
        else:
            self.show_status_message("⚠️ 加载失败，使用默认配置", is_error=True)
        
        return success
    
    def save_config(self) -> bool:
        """保存配置（供run_flet调用）"""
        # 从UI收集数据到Service
        self._update_service_from_ui()
        
        config_field = self.get_component("config_file_field")
        save_path = config_field.value if config_field else "config.json"
        
        success = self.service.save_config(save_path)
        
        if success:
            self._show_save_success()
            self.show_status_message(f"✅ 配置已保存到: {save_path}", is_error=False)
        else:
            self.show_status_message("❌ 保存失败，请检查文件权限", is_error=True)
        
        return success
    
    def scan_templates(self):
        """扫描模板（供run_flet调用）"""
        if not self.service.config:
            self.show_status_message("❌ 请先加载配置", is_error=True)
            return
        
        self.set_refresh_button_loading(True)
        
        # 异步扫描
        def scan_async():
            templates = self.service.scan_templates(self.service.config.template_dir)
            
            def update_ui():
                self._update_template_list(templates, f"✅ 扫描成功，找到 {len(templates)} 个模板")
                self.set_refresh_button_loading(False)
            
            self.page.run_task(update_ui)
        
        thread = threading.Thread(target=scan_async, daemon=True)
        thread.start()
    
    def get_current_config(self) -> Optional[Dict]:
        """获取当前配置（供GeneratorPage使用）"""
        return self.service.get_config_dict()
    
    # ==================== 内部方法（UI更新） ====================
    
    def _update_ui_from_service(self):
        """从Service更新UI"""
        if not self.service.config:
            return
        
        self.get_component("output_dir_field").value = self.service.config.output_dir
        self.get_component("template_dir_field").value = self.service.config.template_dir
        self.get_component("default_ns_field").value = self.service.config.default_namespace
        
        self._update_selected_count()
        self.page.update()
    
    def _update_service_from_ui(self):
        """从UI更新Service"""
        if not self.service.config:
            return
        
        self.service.update_config_from_form(
            self.get_component("output_dir_field").value,
            self.get_component("template_dir_field").value,
            self.get_component("default_ns_field").value
        )
    
    def _on_template_checkbox_change(self, filename: str, is_checked: bool):
        """复选框变更"""
        if is_checked:
            self.service.add_template(filename)
            self.show_status_message(f"➕ 已添加: {filename}", is_error=False)
        else:
            self.service.remove_template(filename)
            self.show_status_message(f"➖ 已移除: {filename}", is_error=False)
        
        self._update_selected_count()
    
    # ... 其他辅助方法 ...
    
    # ==================== 注册事件接口 ====================
    
    def register_load_config_event(self, handler: callable):
        load_btn = self.get_component("load_config_btn")
        if load_btn:
            load_btn.on_click = handler
    
    def register_refresh_event(self, handler: callable):
        refresh_btn = self.get_component("refresh_btn")
        if refresh_btn:
            refresh_btn.on_click = handler
    
    def register_save_event(self, handler: callable):
        save_btn = self.get_component("save_btn")
        if save_btn:
            save_btn.on_click = handler
    
    def register_template_dir_change(self, handler: callable):
        template_dir_field = self.get_component("template_dir_field")
        if template_dir_field:
            template_dir_field.on_change = handler