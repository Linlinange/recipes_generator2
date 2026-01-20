
import json
import flet as ft
from pathlib import Path
from src.model.config import Config
from src.dao.template_loader import TemplateLoader
from src.dao.config_dao import ConfigDAO
from src.interfaces.settings_page import SettingsPage
from typing import Optional

class SettingsController:
    def __init__(self, page: SettingsPage):
        self.page = page
        setattr(page.page, '_settings_controller', self)
        self._load_initial_config()
    
    def _load_initial_config(self):
        """初始加载配置和模板列表"""
        try:
            config = ConfigDAO.load("config.json")
            self.page.load_config_ui(config)
            
            # 扫描模板目录
            templates = TemplateLoader.scan_directory(Path(config.template_dir))
            self.page.update_template_list(templates, "✅ 配置加载成功")
            self.page.update_rules_list()
        except Exception as e:
            self.page.show_status_message(f"❌ 加载失败: {e}", is_error=True)
    
    def handle_template_toggle(self, filename: str):
        """处理模板选择状态切换（核心逻辑）"""
        checkbox = self.page._template_checkboxes.get(filename)
        if not checkbox:
            return
        
        is_checked = checkbox.value
        
        if is_checked:
            if filename not in self.page.config.template_files:
                self.page.config.template_files.append(filename)
                self.page.show_status_message(f"➕ 已添加: {filename}")
        else:
            if filename in self.page.config.template_files:
                self.page.config.template_files.remove(filename)
                self.page.show_status_message(f"➖ 已移除: {filename}")
        
        self.page._update_selected_count()
    
    def handle_template_checkbox_change(self, filename: str, is_checked: bool):
        """复选框变更事件处理"""
        # 复用toggle逻辑
        self.handle_template_toggle(filename)
    
    def refresh_template_list(self):
        """刷新模板列表（绑定到刷新按钮）"""
        self.page.set_refresh_button_loading(True)
        try:
            config = self.page.config
            if not config:
                return
            
            templates = TemplateLoader.scan_directory(Path(config.template_dir))
            self.page.update_template_list(templates, f"✅ 扫描成功，找到 {len(templates)} 个模板")
        except Exception as e:
            self.page.show_status_message(f"❌ 扫描失败: {e}", is_error=True)
        finally:
            self.page.set_refresh_button_loading(False)
    
    def save_config(self):
        """保存配置（绑定到保存按钮）"""
        try:
            config_dict = self.page.get_config_from_ui()
            success = ConfigDAO.save(Config.from_dict(config_dict), "config.json")
            
            if success:
                self.page.show_save_success()
                self.page.show_status_message("✅ 配置已保存", is_error=False)
            else:
                self.page.show_status_message("❌ 保存失败，请检查文件权限", is_error=True)
        except Exception as e:
            self.page.show_status_message(f"❌ 保存异常: {e}", is_error=True)