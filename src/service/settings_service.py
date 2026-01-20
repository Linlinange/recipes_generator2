"""
SettingsService - 持有配置数据并提供业务方法
职责：配置的CRUD、模板扫描、验证
"""

from pathlib import Path
from typing import Optional, List, Dict, Any
import json
import threading

from src.model.config import Config
from src.dao.config_dao import ConfigDAO
from src.dao.template_loader import TemplateLoader


class SettingsService:
    """设置业务服务，持有config实例"""
    
    def __init__(self):
        self.config: Optional[Config] = None
        self.is_scanning = False  # 扫描状态
    
    def load_config(self, path: str = "config.json") -> bool:
        """加载配置"""
        try:
            self.config = ConfigDAO.load(path)
            return True
        except Exception:
            self.config = self._get_default_config()
            return False
    
    def save_config(self, path: str = "config.json") -> bool:
        """保存配置"""
        if not self.config:
            return False
        return ConfigDAO.save(self.config, path)
    
    def scan_templates(self, template_dir: str) -> List[Path]:
        """扫描模板目录"""
        try:
            dir_path = Path(template_dir)
            return TemplateLoader.scan_directory(dir_path)
        except Exception:
            return []
    
    def get_config_dict(self) -> Dict[str, Any]:
        """获取配置字典（供其他页面使用）"""
        if not self.config:
            return self._get_default_config().to_dict()
        return self.config.to_dict()
    
    def add_template(self, filename: str):
        """添加模板到配置"""
        if self.config and filename not in self.config.template_files:
            self.config.template_files.append(filename)
    
    def remove_template(self, filename: str):
        """从配置中移除模板"""
        if self.config and filename in self.config.template_files:
            self.config.template_files.remove(filename)
    
    def update_config_from_form(self, output_dir: str, template_dir: str, namespace: str):
        """从表单更新配置"""
        if self.config:
            self.config.output_dir = output_dir
            self.config.template_dir = template_dir
            self.config.default_namespace = namespace
    
    def _get_default_config(self) -> Config:
        """获取默认配置"""
        return Config({
            "output_dir": "./output",
            "template_dir": "./templates",
            "default_namespace": "minecraft:",
            "template_files": [],
            "replacements": []
        })
