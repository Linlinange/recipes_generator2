#!/usr/bin/env python3
"""
正确版：手动验证所有Service（不依赖真实目录）
运行: python tests/verify_services_correct.py
"""

import sys
import os
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

import tempfile
import json
from src.service.settings_service import SettingsService
from src.service.recipe_service import RecipeService
from src.service.localizer_service import LocalizerService
from src.service.home_service import HomeService


def test_settings_service():
    """验证SettingsService（只测配置逻辑）"""
    print("=" * 60)
    print("测试 SettingsService...")
    print("=" * 60)
    
    try:
        service = SettingsService()
        
        # ✅ 1. 初始状态
        assert service.config is None, "❌ 初始config应为None"
        assert service.is_scanning is False, "❌ 初始is_scanning应为False"
        print("✅ 初始状态正确")
        
        # ✅ 2. 创建临时配置（目录字段用"."，保证存在）
        config_data = {
            "output_dir": ".",  # ✅ 当前目录一定存在
            "template_dir": ".",  # ✅ 当前目录一定存在
            "default_namespace": "test:",
            "template_files": ["test.json"],
            "replacements": [{"type": "material", "values": ["iron"], "enabled": True, "description": ""}]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            temp_file = f.name
        
        try:
            # ✅ 3. 加载配置
            success = service.load_config(temp_file)
            assert success is True, "❌ 加载配置应成功"
            assert service.config is not None, "❌ 加载后config不应为None"
            print("✅ 配置加载成功")
            
            # ✅ 4. 验证配置内容
            assert service.config.output_dir == ".", "❌ 输出目录不匹配"
            assert len(service.config.template_files) == 1, "❌ 模板文件数量不匹配"
            print("✅ 配置内容正确")
            
            # ✅ 5. 验证配置（目录存在，应该通过）
            errors = service.validate_config()
            assert len(errors) == 0, f"❌ 配置验证应通过，但得到错误: {errors}"
            print("✅ 配置验证通过")
            
            # ✅ 6. 扫描模板（这才是真正操作文件）
            templates = service.scan_templates(".")
            assert len(templates) > 0, "❌ 当前目录应至少有一个文件"
            print(f"✅ 模板扫描功能正常（扫描到 {len(templates)} 个文件）")
            
            # ✅ 7. 添加模板（只改配置列表，不创建文件）
            initial_count = len(service.config.template_files)
            service.add_template("new.json")
            assert len(service.config.template_files) == initial_count + 1, "❌ 添加模板失败"
            assert "new.json" in service.config.template_files, "❌ 新模板不在列表中"
            print("✅ 添加模板成功（仅配置列表）")
            
            # ✅ 8. 移除模板（只改配置列表，不删除文件）
            service.remove_template("new.json")
            assert len(service.config.template_files) == initial_count, "❌ 移除模板失败"
            assert "new.json" not in service.config.template_files, "❌ 模板仍在列表中"
            print("✅ 移除模板成功（仅配置列表）")
            
        finally:
            os.unlink(temp_file)
        
        print("\n✅ SettingsService 所有测试通过！\n")
        return True
        
    except Exception as e:
        print(f"\n❌ SettingsService 测试失败: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_recipe_service():
    """验证RecipeService（用Mock，不依赖真实目录）"""
    print("=" * 60)
    print("测试 RecipeService...")
    print("=" * 60)
    
    try:
        from unittest.mock import MagicMock
        
        # ✅ 创建Mock SettingsService（返回的配置不需要真实目录）
        mock_settings = MagicMock()
        mock_settings.get_config_dict.return_value = {
            "output_dir": "./test_output",  # ✅ 无需真实存在
            "template_dir": "./test_templates",  # ✅ 无需真实存在
            "default_namespace": "minecraft:",
            "template_files": ["test.json"],  # ✅ 无需真实存在
            "replacements": [{"type": "material", "values": ["iron"], "enabled": True, "description": ""}]
        }
        
        # ✅ 1. 带SettingsService初始化
        service = RecipeService(settings_service=mock_settings)
        assert service.settings_service is mock_settings, "❌ SettingsService未正确注入"
        assert service.config is not None, "❌ 配置未自动加载"
        print("✅ 带SettingsService初始化成功")
        
        # ✅ 2. 验证不是单例
        service2 = RecipeService(settings_service=mock_settings)
        assert service is not service2, "❌ 单例模式未移除！"
        print("✅ 确认不是单例模式")
        
        # ✅ 3. 不带SettingsService初始化
        service_no_settings = RecipeService(settings_service=None)
        assert service_no_settings.config is None, "❌ 不带SettingsService时应无配置"
        print("✅ 不带SettingsService初始化正确")
        
        # ✅ 4. 重新加载配置（Mock不关心路径是否存在）
        mock_settings.get_config_dict.reset_mock()
        result = service.reload_config()
        assert result is True, "❌ 重新加载配置应成功"
        assert mock_settings.get_config_dict.call_count == 1, "❌ 应调用一次get_config_dict"
        print("✅ 重新加载配置成功")
        
        # ✅ 5. 没有配置时启动失败
        result = service_no_settings.start_generation()
        assert result is False, "❌ 无配置时应启动失败"
        print("✅ 无配置时启动失败（预期行为）")
        
        # ✅ 6. 设置回调
        mock_callback = MagicMock()
        service.set_callbacks(on_progress=mock_callback)
        assert service.on_progress is mock_callback, "❌ 回调未设置"
        print("✅ 回调设置成功")
        
        # ✅ 7. 验证日志回调
        service._log("测试消息")
        mock_callback.assert_called_once_with("测试消息"), "❌ 回调未正确调用"
        print("✅ 日志回调工作正常")
        
        print("\n✅ RecipeService 所有测试通过！\n")
        return True
        
    except Exception as e:
        print(f"\n❌ RecipeService 测试失败: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_localizer_service():
    """验证LocalizerService（不依赖真实目录）"""
    print("=" * 60)
    print("测试 LocalizerService...")
    print("=" * 60)
    
    try:
        from unittest.mock import MagicMock
        
        # ✅ 创建Mock SettingsService
        mock_settings = MagicMock()
        mock_settings.get_config_dict.return_value = {
            "target_languages": ["en_us", "zh_cn"],
            "source_lang_dir": "./lang",
            "output_lang_dir": "./output/lang"
        }
        
        # ✅ 1. 带SettingsService初始化
        service = LocalizerService(settings_service=mock_settings)
        assert service.settings_service is mock_settings, "❌ SettingsService未正确注入"
        assert service.config is not None, "❌ 配置未自动加载"
        assert "target_languages" in service.config, "❌ 配置结构错误"
        assert service.config["target_languages"] == ["en_us", "zh_cn"], "❌ 配置内容错误"
        print("✅ 带SettingsService初始化成功")
        
        # ✅ 2. 不带SettingsService初始化
        service_no_settings = LocalizerService(settings_service=None)
        assert service_no_settings.config is None, "❌ 不带SettingsService时应无配置"
        print("✅ 不带SettingsService初始化正确")
        
        # ✅ 3. 重新加载配置
        mock_settings.get_config_dict.reset_mock()
        result = service.reload_config()
        assert result is True, "❌ 重新加载配置应成功"
        assert mock_settings.get_config_dict.call_count == 1, "❌ 应调用一次get_config_dict"
        print("✅ 重新加载配置成功")
        
        # ✅ 4. 配置隔离性
        service.config["target_languages"] = ["fr_fr"]
        service2 = LocalizerService(settings_service=mock_settings)
        assert service2.config["target_languages"] == ["en_us", "zh_cn"], "❌ 配置隔离失败"
        print("✅ 配置隔离性验证通过")
        
        # ✅ 5. 占位功能测试（不依赖真实文件）
        result = service.process_translation("test.json")
        assert result is True, "❌ 处理翻译应成功（占位）"
        print("✅ 处理翻译占位功能正常")
        
        print("\n✅ LocalizerService 所有测试通过！\n")
        return True
        
    except Exception as e:
        print(f"\n❌ LocalizerService 测试失败: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_home_service():
    """验证HomeService"""
    print("=" * 60)
    print("测试 HomeService...")
    print("=" * 60)
    
    try:
        service = HomeService()
        
        # ✅ 1. 初始状态
        assert service.app_name == "MC Recipe Generator", "❌ 应用名称错误"
        assert service.app_version == "1.2.0", "❌ 版本号错误"
        print("✅ 初始化正确")
        
        # ✅ 2. 获取应用信息
        info = service.get_app_info()
        assert "name" in info, "❌ 应用信息缺少name"
        assert "version" in info, "❌ 应用信息缺少version"
        assert "python_version" in info, "❌ 应用信息缺少python_version"
        assert "flet_version" in info, "❌ 应用信息缺少flet_version"
        assert info["status"] == "running", "❌ 状态错误"
        print("✅ 应用信息获取成功")
        
        # ✅ 3. 获取统计
        stats = service.get_recent_stats()
        assert isinstance(stats, dict), "❌ 统计结果应为字典"
        assert "total_generated" in stats, "❌ 统计缺少total_generated"
        assert "template_count" in stats, "❌ 统计缺少template_count"
        assert "run_count" in stats, "❌ 统计缺少run_count"
        print("✅ 统计功能正常")
        
        # ✅ 4. 欢迎消息
        message = service.get_welcome_message()
        assert "MC Recipe Generator" in message, "❌ 欢迎消息不包含应用名"
        assert "1.2.0" in message, "❌ 欢迎消息不包含版本"
        print("✅ 欢迎消息正常")
        
        print("\n✅ HomeService 所有测试通过！\n")
        return True
        
    except Exception as e:
        print(f"\n❌ HomeService 测试失败: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行所有验证（修正版）"""
    print("\n" + "=" * 60)
    print("最终版：验证所有Service（正确分离逻辑）")
    print("=" * 60 + "\n")
    
    results = []
    
    # 按依赖顺序测试
    results.append(("SettingsService", test_settings_service()))
    results.append(("RecipeService", test_recipe_service()))
    results.append(("LocalizerService", test_localizer_service()))
    results.append(("HomeService", test_home_service()))
    
    # 打印总结
    print("=" * 60)
    print("验证总结:")
    print("=" * 60)
    
    for name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{name:20s} {status}")
    
    all_passed = all(passed for _, passed in results)
    
    if all_passed:
        print("\n🎉 所有Service验证通过！")
        print("\n验证要点：")
        print("  ✅ 依赖注入正常工作")
        print("  ✅ 单例模式已移除")
        print("  ✅ 配置列表操作与文件操作分离")
        print("  ✅ 设置职责边界：Service管配置，DAO/Loader管文件")
        return 0
    else:
        print("\n⚠️  部分Service验证失败，请检查错误信息")
        return 1


if __name__ == '__main__':
    sys.exit(main())