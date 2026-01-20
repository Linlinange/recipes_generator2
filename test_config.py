import unittest
from src.model.config import Config, ReplacementRule


class TestReplacementRule(unittest.TestCase):
    """测试ReplacementRule序列化和验证"""
    
    def test_create_from_valid_data(self):
        """测试从有效数据创建"""
        data = {
            "type": "tree",
            "values": ["oak", "birch"],
            "extra": {"oak": {"color": "brown"}},
            "enabled": True,
            "description": "Tree types"
        }
        rule = ReplacementRule.create(data)
        
        self.assertEqual(rule.type, "tree")
        self.assertEqual(rule.values, ["oak", "birch"])
        
    def test_to_dict_serialization(self):
        """测试序列化为字典"""
        rule = ReplacementRule(
            type="color",
            values=["red", "blue"],
            extra={"red": {"rgb": "ff0000"}},
            enabled=False,
            description="Color variants"
        )
        
        result = rule.to_dict()
        
        self.assertEqual(result["type"], "color")
        self.assertEqual(result["enabled"], False)


class TestConfig(unittest.TestCase):
    """测试Config的getter/setter和验证"""
    
    def test_from_dict_with_defaults(self):
        """测试从字典创建，使用默认值"""
        config = Config.from_dict({})
        
        self.assertEqual(config.output_dir, "./output")
        self.assertEqual(config.template_files, [])
        
    def test_to_dict_serialization(self):
        """测试完整序列化"""
        raw_data = {
            "output_dir": "./test_output",
            "template_files": ["recipe1.json", "recipe2.json"],
            "replacements": [{"type": "tree", "values": ["oak"]}]
        }
        config = Config.from_dict(raw_data)
        
        result = config.to_dict()
        
        self.assertEqual(result["output_dir"], "./test_output")
        self.assertEqual(len(result["template_files"]), 2)
        
    def test_template_files_setter_deduplicates(self):
        """测试setter自动去重"""
        config = Config.from_dict({})
        
        config.template_files = ["a.json", "b.json", "a.json"]
        
        self.assertEqual(len(config.template_files), 2)