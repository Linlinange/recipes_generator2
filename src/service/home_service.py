"""
HomeService - 首页业务逻辑
职责：应用元数据、统计数据
"""

import re
from pathlib import Path
from typing import Dict, Any
import sys
import time


class HomeService:
    """单例：首页业务服务"""
    
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
        self.app_name = "MC Recipe Generator"
        self.app_version = self._get_version()
        self.build_time = time.time()
    
    def _get_version(self) -> str:
        """从pyproject.toml获取版本 - 无需tomllib"""
        try:
            project_root = Path(__file__).parent.parent.parent
            pyproject_path = project_root / "pyproject.toml"
            
            if not pyproject_path.exists():
                return "1.0.0"
            
            # 简单正则解析
            content = pyproject_path.read_text(encoding="utf-8")
            
            # 匹配 version = "1.2.3" 或 version = '1.2.3'
            version_match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
            if version_match:
                return version_match.group(1)
            
            # 备用：查找 [tool.poetry] 下的 version
            poetry_match = re.search(
                r'\[tool\.poetry\].*?version\s*=\s*["\']([^"\']+)["\']', 
                content, 
                re.DOTALL
            )
            if poetry_match:
                return poetry_match.group(1)
                
        except Exception:
            pass
        
        return "1.0.0"
    
    def get_app_info(self) -> Dict[str, Any]:
        """获取应用信息"""
        return {
            "name": self.app_name,
            "version": self.app_version,
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "flet_version": self._get_flet_version(),
        }
    
    def _get_flet_version(self) -> str:
        """获取Flet版本"""
        try:
            import flet
            return flet.__version__
        except Exception:
            return "unknown"
    
    def get_recent_stats(self) -> Dict[str, int]:
        """获取最近统计（占位）"""
        output_dir = Path("./output")
        template_dir = Path("./templates")
        
        return {
            "total_generated": len(list(output_dir.glob("*.json"))) if output_dir.exists() else 0,
            "template_count": len(list(template_dir.glob("*.json"))) if template_dir.exists() else 0,
            "run_count": 0,
        }