# src/generator.py
import itertools
import re
from src.config import ConfigManager
from src.template import Template
from src.engine import ReplacementEngine, CombinationGenerator
from src.writer import OutputWriter
from pathlib import Path
from typing import Dict, List

class RecipeGenerator:
    """主生成器（协调器）"""
    
    def __init__(self, config_path: str):
        self.config = ConfigManager(config_path)
        self.engine = ReplacementEngine(self.config)
        self.writer = OutputWriter(self.config.output_dir)
        self.stats = self.writer.stats
    
    def run(self, dry_run: bool = False, explain_mode: bool = False):
        print("\n🚀 开始生成...\n")
        
        templates = self._load_templates()
        
        for template_name, template in templates.items():
            self._process_template(template, dry_run, explain_mode)
        
        self._print_stats()
        
        if dry_run:
            print("⚠️  预览模式，未实际写入文件")
    
    def _load_templates(self) -> Dict[str, Template]:
        template_dir = self.config.template_dir
        templates = {}
        
        for filename in self.config.get("template_files", []):
            path = template_dir / filename
            if path.exists():
                templates[filename] = Template(path)
            else:
                print(f"⚠️  模板不存在: {path}")
        
        return templates
    
    def _process_template(self, template: Template, dry_run: bool, explain_mode: bool):
        """处理单个模板
        
        ✅ 修复：由文件名字符串顺序决定组合生成顺序
        """
        # 1. 从文件名中提取占位符顺序
        filename = template.path.name
        filename_placeholders = self._extract_placeholders_from_filename(filename)
        
        # 2. 按照文件名顺序获取规则
        ordered_rules = []
        for placeholder in filename_placeholders:
            rule = next((r for r in self.config.get_active_rules() if r["type"] == placeholder), None)
            if rule:
                ordered_rules.append(rule)
        
        # 3. 生成组合
        if not ordered_rules:
            return
        
        value_lists = [r["values"] for r in ordered_rules]
        combos = list(itertools.product(*value_lists))
        
        # 4. 生成文件
        placeholder_names = [r["type"] for r in ordered_rules]
        
        for combo in combos:
            combo_dict = dict(zip(placeholder_names, combo))
            self._generate_single(template, combo_dict, dry_run, explain_mode)
    
    def _extract_placeholders_from_filename(self, filename: str) -> List[str]:
        """从文件名中提取占位符（保持字面顺序）"""
        pattern = re.compile(r"\{([a-zA-Z0-9_]+)\}")
        return pattern.findall(filename)
    
    def _generate_single(self, template: Template, combo_dict: Dict, dry_run: bool, explain_mode: bool):
        resolved_filename = self.engine.apply(template.path.name, combo_dict, None)
        safe_filename = resolved_filename.replace(":", "_")
        
        explain_log = [] if explain_mode else None
        content = self.engine.apply(template.content, combo_dict, explain_log)
        
        if dry_run:
            print(f"📄 [预览] {safe_filename}")
        
        self.writer.write(safe_filename, content, dry_run=dry_run)
        
        if explain_mode and explain_log:
            print(f"\n📝 组合: {combo_dict}")
            for log in explain_log:
                print(log)
    
    def _print_stats(self):
        print(f"\n=== 🎯 生成完成 ===")
        print(f"总数: {self.stats['total']} 个文件")