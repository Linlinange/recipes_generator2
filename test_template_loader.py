import unittest
from pathlib import Path
import tempfile
from unittest.mock import patch
from src.dao.template_loader import TemplateLoader


class TestTemplateLoader(unittest.TestCase):
    """测试模板加载和目录扫描"""
    
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.temp_dir.name)
    
    def tearDown(self):
        self.temp_dir.cleanup()
    
    def test_init_validates_directory_exists(self):
        """测试初始化时验证目录存在"""
        with self.assertRaises(FileNotFoundError):
            TemplateLoader(Path("/non/existent/path"))
    
    def test_scan_directory_returns_sorted_list(self):
        """测试扫描返回排序后的列表"""
        # 创建乱序文件
        (self.tmp_path / "zebra.json").touch()
        (self.tmp_path / "apple.json").touch()
        
        paths = TemplateLoader.scan_directory(self.tmp_path)
        
        names = [p.name for p in paths]
        self.assertEqual(names, ["apple.json", "zebra.json"])
    
    def test_scan_directory_returns_json_only(self):
        """测试只返回.json文件"""
        (self.tmp_path / "recipe.json").touch()
        (self.tmp_path / "readme.txt").touch()
        
        paths = TemplateLoader.scan_directory(self.tmp_path)
        
        self.assertEqual(len(paths), 1)
        self.assertEqual(paths[0].name, "recipe.json")