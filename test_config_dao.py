import unittest
import json
import tempfile
from pathlib import Path
from src.dao.config_dao import ConfigDAO
from src.model.config import Config


class TestConfigDAO(unittest.TestCase):
    """测试配置的加载和保存"""
    
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.temp_dir.name)
    
    def tearDown(self):
        self.temp_dir.cleanup()
    
    def test_load_valid_config(self):
        """测试加载有效配置"""
        config_data = {
            "output_dir": "./output",
            "template_files": ["test.json"],
            "replacements": [{"type": "tree", "values": ["oak"]}]
        }
        config_path = self.tmp_path / "config.json"
        config_path.write_text(json.dumps(config_data), encoding="utf-8")
        
        config = ConfigDAO.load(str(config_path))
        
        self.assertEqual(config.output_dir, "./output")
        self.assertIn("test.json", config.template_files)
    
    def test_load_file_not_found(self):
        """测试配置文件不存在"""
        with self.assertRaises(FileNotFoundError):
            ConfigDAO.load("nonexistent.json")
    
    def test_save_valid_config(self):
        """测试保存有效配置"""
        config_path = self.tmp_path / "saved_config.json"
        
        config = Config.from_dict({
            "output_dir": "./test_output",
            "template_files": ["recipe.json"]
        })
        
        success = ConfigDAO.save(config, str(config_path))
        
        self.assertTrue(success)
        self.assertTrue(config_path.exists())