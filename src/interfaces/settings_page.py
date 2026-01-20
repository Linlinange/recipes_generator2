
import flet as ft
from pathlib import Path
import json
from typing import Optional
from src.interfaces.base_page import BasePage
from src.model.config import Config

class SettingsPage(BasePage):
    """设置页 - 可视化编辑config.json"""
    
    def __init__(self, router, page: ft.Page):
        super().__init__(router, page)
        self.config: Optional[Config] = None
    
    def load_config(self) -> Config:
        """从文件加载配置"""
        try:
            config_path = Path("config.json")
            if config_path.exists():
                raw_data = json.loads(config_path.read_text(encoding='utf-8'))
                return Config(raw_data)
            return self.get_default_config()
        except Exception as e:
            print(f"加载配置失败: {e}")
            return self.get_default_config()
    
    def get_default_config(self) -> Config:
        """返回默认配置"""
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
        
        # 表单字段
        self.add_component("output_dir_field", ft.TextField(
            value=self.config.output_dir,
            label="输出目录",
            expand=True,
            on_change=self._on_output_dir_change
        ))
        
        self.add_component("template_dir_field", ft.TextField(
            value=self.config.template_dir,
            label="模板目录",
            expand=True,
            on_change=self._on_template_dir_change
        ))
        
        self.add_component("default_ns_field", ft.TextField(
            value=self.config.default_namespace,
            label="默认命名空间",
            expand=True,
            on_change=self._on_namespace_change
        ))
        
        # 模板文件列表
        self.add_component("template_files_list", ft.ListView(
            spacing=5,
            padding=10,
            auto_scroll=True,
            height=200,
        ))
        self._refresh_template_files()
        
        # 模板按钮
        self.add_component("add_template_btn", ft.ElevatedButton(
            "添加模板文件",
            icon=ft.icons.ADD,
            on_click=lambda e: self._add_template_file()
        ))
        self.add_component("remove_template_btn", ft.ElevatedButton(
            "移除选中",
            icon=ft.icons.REMOVE,
            on_click=lambda e: self._remove_selected_template()
        ))
        
        # 替换规则列表
        self.add_component("rules_list", ft.ListView(
            spacing=5,
            padding=10,
            height=200,
        ))
        self._refresh_rules_list()
        
        # 保存按钮（关键！绑定在控制器中）
        self.add_component("save_btn", ft.ElevatedButton(
            "💾 保存配置",
            expand=True,
            bgcolor=ft.colors.BLUE,
            color="white",
        ))
        
        # 布局
        return ft.Container(
            content=ft.Column([
                ft.Text("⚙️ 配置文件设置", size=24, weight=ft.FontWeight.BOLD),
                ft.Text("基础设置", size=18, weight=ft.FontWeight.BOLD),
                self.get_component("output_dir_field"),
                self.get_component("template_dir_field"),
                self.get_component("default_ns_field"),
                ft.Divider(),
                ft.Text("模板文件", size=18, weight=ft.FontWeight.BOLD),
                self.get_component("template_files_list"),
                ft.Row([
                    self.get_component("add_template_btn"),
                    self.get_component("remove_template_btn"),
                ], spacing=10),
                ft.Divider(),
                ft.Text("替换规则", size=18, weight=ft.FontWeight.BOLD),
                self.get_component("rules_list"),
                ft.Divider(),
                self.get_component("save_btn"),
            ], expand=True, spacing=15, scroll=ft.ScrollMode.AUTO),
            padding=ft.padding.all(20),
        )
    
    # ==================== 内部方法 ====================
    
    def _on_output_dir_change(self, e: ft.ControlEvent):
        if self.config:
            self.config.output_dir = e.control.value
            print(f"输出目录改为: {self.config.output_dir}")
    
    def _on_template_dir_change(self, e: ft.ControlEvent):
        if self.config:
            self.config.template_dir = e.control.value
            print(f"模板目录改为: {self.config.template_dir}")
            self._refresh_template_files()
    
    def _on_namespace_change(self, e: ft.ControlEvent):
        if self.config:
            self.config.default_namespace = e.control.value
            print(f"命名空间改为: {self.config.default_namespace}")
    
    def _refresh_template_files(self):
        """刷新模板文件列表"""
        list_view = self.get_component("template_files_list")
        if not list_view or not self.config:
            return
        
        list_view.controls.clear()
        template_dir = Path(self.config.template_dir)
        
        if template_dir.exists():
            # 显示已配置的模板
            for file in self.config.template_files:
                list_view.controls.append(ft.ListTile(
                    title=ft.Text(file),
                    leading=ft.Icon(ft.icons.DESCRIPTION),
                    selected=False,
                ))
            
            # 显示未添加的模板（灰色）
            existing_files = set(self.config.template_files)
            for file in sorted(template_dir.glob("*.json")):
                if file.name not in existing_files:
                    list_view.controls.append(ft.ListTile(
                        title=ft.Text(file.name, color=ft.colors.GREY_400),
                        leading=ft.Icon(ft.icons.DESCRIPTION, color=ft.colors.GREY_400),
                        on_click=lambda e, f=file.name: self._quick_add_template(f),
                    ))
        
        # 延迟到控制器初始化后再update
        if hasattr(self.page, 'page'):
            self.page.page.update()
    
    def _quick_add_template(self, filename: str):
        """快速添加模板"""
        if self.config and filename not in self.config.template_files:
            self.config.template_files.append(filename)
            self._refresh_template_files()
            print(f"✅ 快速添加模板: {filename}")
    
    def _add_template_file(self):
        """手动添加模板（待实现对话框）"""
        print("🚧 文件选择对话框待实现")
    
    def _remove_selected_template(self):
        """移除选中的模板（待实现多选）"""
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
            list_view.controls.append(ft.ListTile(
                title=ft.Text(f"规则 {i+1}: {rule.type}"),
                subtitle=ft.Text(f"{len(rule.values)} 个值"),
                leading=ft.Icon(ft.icons.LIST_ALT),
                trailing=ft.IconButton(ft.icons.EDIT, on_click=lambda e, idx=i: self._edit_rule(idx)),
            ))
        
        if hasattr(self.page, 'page'):
            self.page.page.update()
    
    def _edit_rule(self, index: int):
        """编辑规则（待实现对话框）"""
        print(f"编辑规则 {index}")
    
    # ==================== 核心方法 ====================
    
    def get_config(self) -> dict:
        """从UI收集配置数据，返回dict"""
        if not self.config:
            raise ValueError("配置未加载")
        
        return {
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
    
    def save_config(self) -> bool:
        """保存配置到文件（由控制器调用）"""
        if not self.config:
            return False
        
        try:
            config_dict = self.get_config()
            Path("config.json").write_text(
                json.dumps(config_dict, indent=2, ensure_ascii=False),
                encoding='utf-8'
            )
            return True
        except Exception as e:
            print(f"保存配置失败: {e}")
            return False