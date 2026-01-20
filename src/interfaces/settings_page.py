# src/interfaces/settings_page.py
import flet as ft
from pathlib import Path
import json
from typing import Callable, Optional
from src.interfaces.base_page import BasePage
from src.model.config import Config, ReplacementRule

class SettingsPage(BasePage):
    """设置页 - 可视化编辑config.json"""
    
    def __init__(self, router, page: ft.Page):
        super().__init__(router, page)
        self.config: Optional[Config] = None
    
    def load_config(self) -> Config:
        """从文件加载配置为Config实例"""
        try:
            config_path = Path("config.json")
            if config_path.exists():
                raw_data = json.loads(config_path.read_text(encoding='utf-8'))
                return Config(raw_data)
            else:
                return self.get_default_config()
        except Exception as e:
            print(f"加载配置失败: {e}")
            return self.get_default_config()
    
    def get_default_config(self) -> Config:
        """返回默认Config实例"""
        return Config({
            "output_dir": "./output",
            "template_dir": "./templates",
            "default_namespace": "minecraft:",
            "template_files": [],
            "replacements": []
        })
    
    def build(self) -> ft.Control:
        """构建设置表单"""
        self.config = self.load_config()
        
        # 创建表单组件
        output_dir_field = self.add_component(
            "output_dir_field",
            ft.TextField(
                value=self.config.output_dir,  # 使用Config的属性
                label="输出目录",
                expand=True,
                on_change=lambda e: self._on_output_dir_change(e)
            )
        )
        
        template_dir_field = self.add_component(
            "template_dir_field",
            ft.TextField(
                value=self.config.template_dir,  # 使用Config的属性
                label="模板目录",
                expand=True,
                on_change=lambda e: self._on_template_dir_change(e)
            )
        )
        
        default_ns_field = self.add_component(
            "default_ns_field",
            ft.TextField(
                value=self.config.default_namespace,  # 使用Config的属性
                label="默认命名空间",
                expand=True,
                on_change=lambda e: self._on_namespace_change(e)
            )
        )
        
        # 模板文件列表（可编辑）
        template_files_list = self.add_component(
            "template_files_list",
            ft.ListView(
                spacing=5,
                padding=10,
                auto_scroll=True,
                height=200,
            )
        )
        
        # 加载模板文件
        self._refresh_template_files()
        
        # 模板操作按钮
        add_template_btn = self.add_component(
            "add_template_btn",
            ft.ElevatedButton("添加模板文件", icon=ft.icons.ADD, on_click=lambda e: self._add_template_file())
        )
        
        remove_template_btn = self.add_component(
            "remove_template_btn",
            ft.ElevatedButton("移除选中", icon=ft.icons.REMOVE, on_click=lambda e: self._remove_selected_template())
        )
        
        # 替换规则列表
        rules_list = self.add_component(
            "rules_list",
            ft.ListView(
                spacing=5,
                padding=10,
                height=200,
            )
        )
        
        self._refresh_rules_list()
        
        # 保存按钮
        save_btn = self.add_component(
            "save_btn",
            ft.ElevatedButton(
                "💾 保存配置",
                expand=True,
                bgcolor=ft.colors.GREEN,
                color="white",
            )
        )
        
        # 布局
        return ft.Container(
            content=ft.Column([
                ft.Text("⚙️ 配置文件设置", size=24, weight=ft.FontWeight.BOLD),
                
                ft.Text("基础设置", size=18, weight=ft.FontWeight.BOLD),
                output_dir_field,
                template_dir_field,
                default_ns_field,
                
                ft.Divider(),
                
                ft.Text("模板文件", size=18, weight=ft.FontWeight.BOLD),
                template_files_list,
                ft.Row([add_template_btn, remove_template_btn], spacing=10),
                
                ft.Divider(),
                
                ft.Text("替换规则", size=18, weight=ft.FontWeight.BOLD),
                rules_list,
                
                ft.Divider(),
                
                save_btn,
            ], expand=True, spacing=15, scroll=ft.ScrollMode.AUTO),
            padding=ft.padding.all(20),
        )
    
    # ==================== 事件处理 ====================
    
    def _on_output_dir_change(self, e):
        """输出目录变更"""
        if self.config:
            self.config.output_dir = e.control.value
            print(f"输出目录改为: {self.config.output_dir}")
    
    def _on_template_dir_change(self, e):
        """模板目录变更"""
        if self.config:
            self.config.template_dir = e.control.value
            print(f"模板目录改为: {self.config.template_dir}")
            # 自动刷新模板列表
            self._refresh_template_files()
    
    def _on_namespace_change(self, e):
        """命名空间变更"""
        if self.config:
            self.config.default_namespace = e.control.value
            print(f"命名空间改为: {self.config.default_namespace}")
    
    def _refresh_template_files(self):
        """刷新模板文件列表"""
        list_view = self.get_component("template_files_list")
        if not list_view or not self.config:
            return
        
        list_view.controls.clear()
        
        # 从目录扫描模板文件
        template_dir = Path(self.config.template_dir)
        if template_dir.exists():
            # 显示已配置的模板文件
            for file in self.config.template_files:
                list_view.controls.append(
                    ft.ListTile(
                        title=ft.Text(file),
                        leading=ft.Icon(ft.icons.DESCRIPTION),
                        selected=False,
                    )
                )
            
            # 显示目录中所有模板（灰色，未添加的）
            existing_files = set(self.config.template_files)
            for file in sorted(template_dir.glob("*.json")):
                if file.name not in existing_files:
                    list_view.controls.append(
                        ft.ListTile(
                            title=ft.Text(file.name, color=ft.colors.GREY_400),
                            leading=ft.Icon(ft.icons.DESCRIPTION, color=ft.colors.GREY_400),
                            on_click=lambda e, f=file.name: self._quick_add_template(f),
                        )
                    )
        
        self.page.update()
    
    def _quick_add_template(self, filename: str):
        """快速添加模板文件"""
        if self.config and filename not in self.config.template_files:
            self.config.template_files.append(filename)
            self._refresh_template_files()
            print(f"✅ 快速添加模板: {filename}")
    
    def _add_template_file(self):
        """手动添加模板文件（弹出对话框）"""
        # 这里可以弹出文件选择对话框
        print("🚧 文件选择对话框待实现")
        # TODO: 使用ft.FilePicker
    
    def _remove_selected_template(self):
        """移除选中的模板文件"""
        # TODO: 实现多选删除
        print("🚧 多选删除待实现")
    
    def _refresh_rules_list(self):
        """刷新替换规则列表"""
        list_view = self.get_component("rules_list")
        if not list_view or not self.config:
            return
        
        list_view.controls.clear()
        
        if not self.config.rules:
            list_view.controls.append(ft.Text("暂无替换规则", color=ft.colors.GREY, size=14))
            return
        
        for i, rule in enumerate(self.config.rules):
            # 使用ReplacementRule的类型提示
            rule_type = rule.type
            values_count = len(rule.values)
            
            list_view.controls.append(
                ft.ListTile(
                    title=ft.Text(f"规则 {i+1}: {rule_type}"),
                    subtitle=ft.Text(f"{values_count} 个值"),
                    leading=ft.Icon(ft.icons.LIST_ALT),
                    trailing=ft.IconButton(ft.icons.EDIT, on_click=lambda e, idx=i: self._edit_rule(idx)),
                )
            )
        
        self.page.update()
    
    def _edit_rule(self, index: int):
        """编辑规则（弹出对话框）"""
        print(f"编辑规则 {index}")
        # TODO: 实现规则编辑对话框
    
    # ==================== 事件注册方法 ====================
    
    def register_save_event(self, handler: Callable):
        """注册保存按钮点击事件"""
        self.register_event("save_btn", "click", handler)
    
    def register_template_dir_change(self, handler: Callable):
        """注册模板目录变更事件"""
        self.register_event("template_dir_field", "change", handler)
    
    def register_output_dir_change(self, handler: Callable):
        """注册输出目录变更事件"""
        self.register_event("output_dir_field", "change", handler)
    
    def register_default_ns_change(self, handler: Callable):
        """注册命名空间变更事件"""
        self.register_event("default_ns_field", "change", handler)
    
    def register_add_template_event(self, handler: Callable):
        """注册添加模板事件"""
        self.register_event("add_template_btn", "click", handler)
    
    def register_remove_template_event(self, handler: Callable):
        """注册移除模板事件"""
        self.register_event("remove_template_btn", "click", handler)
    
    def save_config(self) -> bool:
        """保存配置到文件"""
        if not self.config:
            return False
        
        try:
            config_path = Path("config.json")
            # Config类可以序列化回字典
            config_dict = {
                "output_dir": self.config.output_dir,
                "template_dir": self.config.template_dir,
                "default_namespace": self.config.default_namespace,
                "template_files": self.config.template_files,
                "replacements": [
                    {
                        "type": rule.type,
                        "values": rule.values,
                        "extra": rule.extra,
                        "enabled": rule.enabled,
                        "description": rule.description,
                    }
                    for rule in self.config.rules
                ]
            }
            
            config_path.write_text(
                json.dumps(config_dict, indent=2, ensure_ascii=False),
                encoding='utf-8'
            )
            return True
            
        except Exception as e:
            print(f"保存配置失败: {e}")
            return False