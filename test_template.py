import unittest
from pathlib import Path
import tempfile
from src.model.template import Template


class TestTemplate(unittest.TestCase):
    """测试Template模型的占位符提取和异常处理"""
    
    def setUp(self):
        """每个测试前创建临时目录"""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.temp_dir.name)
    
    def tearDown(self):
        """每个测试后清理"""
        self.temp_dir.cleanup()
    
    def test_extract_placeholders_basic(self):
        """测试基本占位符提取"""
        template_content = """
        {
            "type": "minecraft:crafting_shaped",
            "key": {
                "#": {"item": "{tree}_planks"}
            },
            "result": {
                "item": "{modid}:{tree}_door"
            }
        }
        """
        template_file = self.tmp_path / "test_template.json"
        template_file.write_text(template_content, encoding="utf-8")
        
        template = Template(template_file)
        
        self.assertIn("tree", template.placeholders)
        self.assertEqual(len(template.placeholders), 1)
        self.assertEqual(template.placeholders[0], "tree")
    
    def test_extract_placeholders_excludes_modid(self):
        """测试排除modid和modid_safe固定占位符"""
        template_content = """
        {
            "result": {
                "item": "{modid}:{tree}_{modid_safe}_door"
            }
        }
        """
        template_file = self.tmp_path / "test_template.json"
        template_file.write_text(template_content, encoding="utf-8")
        
        template = Template(template_file)
        
        self.assertIn("tree", template.placeholders)
        self.assertNotIn("modid", template.placeholders)
        self.assertNotIn("modid_safe", template.placeholders)
    
    def test_load_content_handles_encoding_error(self):
        """测试处理非UTF-8文件异常"""
        template_file = self.tmp_path / "invalid_encoding.json"
        template_file.write_bytes(b"\xff\xfe invalid utf-8 content")
        
        with self.assertRaises(UnicodeDecodeError):
            Template(template_file)
    
    def test_load_content_handles_file_not_found(self):
        """测试处理文件不存在异常"""
        non_existent = self.tmp_path / "missing.json"
        
        with self.assertRaises(FileNotFoundError):
            Template(non_existent)