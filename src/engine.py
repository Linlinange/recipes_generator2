# src/engine.py
import itertools
from typing import Dict, List, Set, Tuple, Any, Optional
from collections import defaultdict

class NamespaceResolver:
    """
    命名空间解析器
    职责：解析值的命名空间信息
    对应原函数：parse_namespace()
    """
    
    @staticmethod
    def resolve(value: str, default_namespace: str) -> Tuple[str, str, str]:
        """
        解析命名空间
        Returns: (纯名称, 完整命名空间, 安全命名空间)
        """
        if ":" in value:
            ns, name = value.split(":", 1)
            full_ns = f"{ns}:"
            safe_ns = f"{ns}_"
        else:
            name = value
            full_ns = default_namespace
            safe_ns = "" if full_ns == "minecraft:" else full_ns.replace(":", "_")
        
        return name, full_ns, safe_ns

class CombinationGenerator:
    """
    组合生成器
    职责：生成笛卡尔积组合
    对应原函数：generate_combinations()
    """
    
    @staticmethod
    def generate(rules: List[Dict], needed_types: Set[str]) -> List[Tuple]:
        """生成所有组合"""
        active_rules = [r for r in rules if r["type"] in needed_types]
        if not active_rules:
            return []
        
        type_names = [r["type"] for r in active_rules]
        value_lists = [r["values"] for r in active_rules]
        
        return list(itertools.product(*value_lists))

class ReplacementEngine:
    """
    替换引擎（核心）
    职责：执行占位符替换逻辑
    对应原函数：apply_replacements()
    """
    
    def __init__(self, config):
        self.config = config
        self.resolver = NamespaceResolver()
    
    def apply(self, content: str, combo: Dict[str, str], 
              explain_log: Optional[list] = None) -> str:
        """
        应用所有替换规则
        
        Args:
            content: 模板内容
            combo: 当前组合字典 {"tree": "oak", "tool": "sword"}
            explain_log: 解释日志（可选）
        """
        # 1. 解析命名空间
        type_info = self._parse_combo(combo)
        
        # 2. 基础替换
        result = self._apply_basic(content, combo, type_info, explain_log)
        
        # 3. 额外规则替换
        result = self._apply_extra(result, combo, type_info, explain_log)
        
        return result
    
    def _parse_combo(self, combo: Dict[str, str]) -> Dict[str, Tuple]:
        """解析组合中所有值的命名空间"""
        info = {}
        for r_type, value in combo.items():
            info[r_type] = self.resolver.resolve(value, self.config.default_namespace)
        return info
    
    def _apply_basic(self, content: str, combo: Dict, info: Dict, 
                     explain_log: Optional[list]) -> str:
        """基础占位符替换"""
        result = content
        
        # 系统占位符
        first_type = next(iter(combo.keys()), None)
        modid = info[first_type][1] if first_type in info else self.config.default_namespace
        modid_safe = "" if modid == "minecraft:" else modid.replace(":", "_")
        
        result = result.replace("{modid}", modid).replace("{modid_safe}", modid_safe)
        
        # 类型占位符
        for r_type, (name, _, _) in info.items():
            placeholder = f"{{{r_type}}}"
            if placeholder in result and explain_log is not None:
                explain_log.append(f"  → 替换 {placeholder} => {name}")
            result = result.replace(placeholder, name)
        
        return result
    
    def _apply_extra(self, content: str, combo: Dict[str, str], info: Dict[str, Tuple],
                    explain_log: Optional[list] = None) -> str:
        """
        应用额外替换规则（extra字段）
        
        匹配优先级（从高到低）：
        1. 完整值匹配（如 "minecraft:bamboo"）
        2. 纯名称匹配（如 "bamboo"）
        3. 通配符匹配（*）
        
        Args:
            content: 待替换的文本内容
            combo: 当前组合字典
            info: 命名空间解析信息
            explain_log: 解释日志列表
            
        Returns:
            应用替换后的内容
        """
        result = content
        
        for rule in self.config.get_active_rules():
            if rule["type"] not in combo:
                continue
            
            r_type = rule["type"]
            info_tuple = info[r_type]
            name = info_tuple[0]              # 纯名称
            namespace = info_tuple[1]         # 完整命名空间
            full_value = f"{namespace}{name}"  # 完整值
            extra = rule.get("extra", {})
            
            # === 优先级1：通配符（最低，最先执行）===
            if "*" in extra:
                for old, new in extra["*"].items():
                    if old in result:
                        if explain_log is not None:
                            explain_log.append(f"  → 通配符替换 [*]: {old} => {new}")
                        result = result.replace(old, new)
            
            # === 优先级2：纯名称匹配（中等）===
            if name in extra:
                for old, new in extra[name].items():
                    if old in result:
                        if explain_log is not None:
                            explain_log.append(f"  → 纯名称匹配 [{name}]: {old} => {new}")
                        result = result.replace(old, new)
            
            # === 优先级3：完整值匹配（最高，最后执行）===
            if full_value in extra:
                for old, new in extra[full_value].items():
                    if old in result:
                        if explain_log is not None:
                            explain_log.append(f"  → 完整值匹配 [{full_value}]: {old} => {new}")
                        result = result.replace(old, new)
        
        return result
