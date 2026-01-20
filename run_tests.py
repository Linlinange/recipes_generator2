#!/usr/bin/env python3
"""
测试运行器 - 使用Python标准库unittest
无需安装任何第三方包
"""
import sys
from pathlib import Path
import unittest

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).parent))

# 导入所有测试
from test_template import TestTemplate
from test_config import TestReplacementRule, TestConfig
from test_template_loader import TestTemplateLoader
from test_config_dao import TestConfigDAO
from test_recipe_service import TestRecipeService

def run_tests():
    """运行所有测试并生成报告"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 加载所有测试类
    suite.addTests(loader.loadTestsFromTestCase(TestTemplate))
    suite.addTests(loader.loadTestsFromTestCase(TestReplacementRule))
    suite.addTests(loader.loadTestsFromTestCase(TestConfig))
    suite.addTests(loader.loadTestsFromTestCase(TestTemplateLoader))
    suite.addTests(loader.loadTestsFromTestCase(TestConfigDAO))
    suite.addTests(loader.loadTestsFromTestCase(TestRecipeService))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 生成简单报告
    print("\n" + "="*70)
    if result.wasSuccessful():
        print(f"✅ 所有测试通过！")
        print(f"运行测试数: {result.testsRun}")
    else:
        print(f"❌ 测试失败！")
        print(f"运行测试数: {result.testsRun}")
        print(f"失败数: {len(result.failures)}")
        print(f"错误数: {len(result.errors)}")
        
        if result.failures:
            print("\n失败详情:")
            for test, traceback in result.failures:
                print(f"  - {test}: {traceback[:200]}...")
        
        if result.errors:
            print("\n错误详情:")
            for test, traceback in result.errors:
                print(f"  - {test}: {traceback[:200]}...")
    print("="*70)
    
    return 0 if result.wasSuccessful() else 1

if __name__ == "__main__":
    sys.exit(run_tests())