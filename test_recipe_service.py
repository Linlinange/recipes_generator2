import unittest
import json
import time
import tempfile
from pathlib import Path
from unittest.mock import Mock
from src.service.recipe_service import RecipeService


class TestRecipeService(unittest.TestCase):
    """测试RecipeService的异步执行和状态管理"""
    
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.temp_dir.name)
        
        # 创建项目结构
        (self.tmp_path / "templates").mkdir()
        (self.tmp_path / "output").mkdir()
        
        # 创建配置
        config_data = {
            "output_dir": str(self.tmp_path / "output"),
            "template_dir": str(self.tmp_path / "templates"),
            "default_namespace": "minecraft:",
            "template_files": ["recipe.json"],
            "replacements": [{"type": "tree", "values": ["oak", "birch"]}]
        }
        self.config_path = self.tmp_path / "config.json"
        self.config_path.write_text(json.dumps(config_data), encoding="utf-8")
        
        # 创建模板
        template = self.tmp_path / "templates" / "recipe.json"
        template.write_text('{"result": {"item": "{tree}"}}', encoding="utf-8")
    
    def tearDown(self):
        self.temp_dir.cleanup()
    
    def test_is_running_property(self):
        """测试运行状态属性"""
        service = RecipeService(str(self.config_path))
        
        self.assertFalse(service.is_running)
        
        service._is_running = True
        self.assertTrue(service.is_running)
    
    def test_run_async_completes_successfully(self):
        """测试异步任务成功完成"""
        service = RecipeService(str(self.config_path))
        
        complete_calls = []
        
        def capture_complete(stats):
            complete_calls.append(stats)
        
        service.on_complete = capture_complete
        
        service.run_async(dry_run=True)
        
        # 等待任务完成
        timeout = 5
        start = time.time()
        while service.is_running and (time.time() - start < timeout):
            time.sleep(0.1)
        
        self.assertFalse(service.is_running)
        self.assertEqual(len(complete_calls), 1)
    
    def test_cancel_stops_execution(self):
        """测试取消停止执行"""
        service = RecipeService(str(self.config_path))
        
        progress_calls = []
        
        def capture_progress(msg):
            progress_calls.append(msg)
            if "已取消" in msg:
                service._cancel_requested = False  # 重置
        
        service.on_progress = capture_progress
        
        service.run_async()
        time.sleep(0.1)  # 让任务启动
        service.cancel()
        
        # 等待取消完成
        timeout = 3
        start = time.time()
        while service.is_running and (time.time() - start < timeout):
            time.sleep(0.1)
        
        self.assertFalse(service.is_running)
        self.assertTrue(any("已取消" in str(msg) for msg in progress_calls))