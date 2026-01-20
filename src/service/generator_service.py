"""
GeneratorService - 生成器业务逻辑
职责：持有配置、管理RecipeService、跟踪状态
"""

import json
import threading
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple

from src.service.recipe_service import RecipeService
from src.service.settings_service import SettingsService


class GeneratorService:
    """单例：生成器业务服务"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self.settings_service = SettingsService()  # 获取共享配置
        self.recipe_service: Optional[RecipeService] = None
        self.generation_stats: Dict[str, Any] = {
            "is_running": False,
            "processed_count": 0,
            "total_files": 0,
            "current_template": "",
        }
    
    def start_generation(self, dry_run: bool = False, explain_mode: bool = False) -> bool:
        """开始生成配方"""
        if self.generation_stats["is_running"]:
            return False
        
        # 获取配置
        config_dict = self.settings_service.get_config_dict()
        if not config_dict.get("template_files"):
            return False
        
        # 创建RecipeService
        config_path = self._get_temp_config_path(config_dict)
        self.recipe_service = RecipeService(
            config_path,
            on_progress=self._on_progress,
            on_complete=self._on_complete,
            on_error=self._on_error
        )
        
        # 启动异步任务
        self.generation_stats["is_running"] = True
        self.generation_stats["processed_count"] = 0
        self.recipe_service.run_async(dry_run=dry_run, explain_mode=explain_mode)
        return True
    
    def cancel_generation(self):
        """取消生成"""
        if self.recipe_service:
            self.recipe_service.cancel()
    
    def get_status(self) -> Dict[str, Any]:
        """获取生成状态"""
        if self.recipe_service:
            return self.recipe_service.status
        return self.generation_stats
    
    def _on_progress(self, message: str):
        """进度回调"""
        # 可在这里添加日志记录
        self.generation_stats["processed_count"] += 1
    
    def _on_complete(self, stats: Dict[str, Any]):
        """完成回调"""
        self.generation_stats["is_running"] = False
        self.generation_stats["total_files"] = stats.get("total", 0)
        self.generation_stats["processed_count"] = stats.get("total", 0)
    
    def _on_error(self, error: Exception):
        """错误回调"""
        self.generation_stats["is_running"] = False
    
    def _get_temp_config_path(self, config_dict: Dict[str, Any]) -> str:
        """创建临时配置文件供RecipeService使用"""
        import tempfile
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        json.dump(config_dict, temp_file, ensure_ascii=False, indent=2)
        temp_file.close()
        return temp_file.name
    
    def preview_combinations(self, limit: int = 5) -> List[Tuple[str, str]]:
        """预览组合"""
        config_dict = self.settings_service.get_config_dict()
        if not config_dict.get("template_files"):
            return []
        
        # 创建临时RecipeService用于预览
        config_path = self._get_temp_config_path(config_dict)
        service = RecipeService(config_path)
        return service.preview_combinations(limit)
    
    def get_output_directory(self) -> str:
        """获取输出目录"""
        config_dict = self.settings_service.get_config_dict()
        return config_dict.get("output_dir", "./output")