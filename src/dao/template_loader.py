
from pathlib import Path
from typing import Dict, List
from src.model.template import Template

class TemplateLoader:
    """模板加载器：只负责从磁盘加载模板文件"""
    
    def __init__(self, template_dir: Path):
        self.template_dir = template_dir
    
    def load_all(self, filenames: List[str]) -> Dict[str, Template]:
        """批量加载模板"""
        templates = {}
        for name in filenames:
            path = self.template_dir / name
            if path.exists():
                templates[name] = Template(path)
            else:
                print(f"⚠️  模板不存在: {path}")
        return templates
    
    def load_single(self, filename: str) -> Template:
        """加载单个模板"""
        path = self.template_dir / filename
        if path.exists():
            return Template(path)
        else:
            raise FileNotFoundError(f"模板不存在: {path}")
    
    @staticmethod
    def scan_directory(directory: Path) -> List[Path]:
        # 参数: 模板目录的Path对象
        # 返回: 该目录下所有 *.json 文件的Path列表（按文件名排序）
        # 备注: 需处理目录不存在、无权限等异常
        pass
