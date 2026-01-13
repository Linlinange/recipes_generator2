# src/generator.py
import json
import re
import itertools
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set, Tuple

class Config:
    """配置管理类：负责加载和提供配置数据
    
    作用类似于 Java 的 Config 或 Properties 类，
    封装了配置的加载、访问和验证逻辑。
    """
    
    def __init__(self, path: str):
        """初始化配置，从 JSON 文件加载数据
        
        Args:
            path: 配置文件路径，如 "config.json"
        """
        self._data = self._load(path)
    
    def _load(self, path: str) -> dict:
        """从指定路径加载 JSON 配置文件
        
        Args:
            path: 配置文件路径
            
        Returns:
            解析后的配置字典
        """
        with Path(path).open("r", encoding="utf-8") as f:
            return json.load(f)
    
    def get(self, key: str, default=None):
        """获取配置项的值（安全访问）
        
        Args:
            key: 配置键名
            default: 默认值（如果键不存在）
            
        Returns:
            配置值或默认值
        """
        return self._data.get(key, default)
    
    @property
    def output_dir(self) -> Path:
        """输出目录路径（懒加载，返回 Path 对象）
        
        Returns:
            Path 对象，便于文件操作
        """
        return Path(self._data.get("output_dir", "./output"))
    
    @property
    def template_dir(self) -> Path:
        """模板目录路径
        
        Returns:
            Path 对象
        """
        return Path(self._data.get("template_dir", "./templates"))
    
    def get_active_rules(self) -> List[dict]:
        """获取所有启用的替换规则
        
        过滤掉 disabled 的规则，避免无效遍历。
        
        Returns:
            启用的替换规则列表
        """
        return [r for r in self._data.get("replacements", []) if r.get("enabled", True)]

class Template:
    """模板类：封装模板文件的加载和占位符扫描
    
    每个模板对象代表一个 JSON 模板文件，
    负责提取其中的动态占位符。
    """
    
    # 正则模式：匹配 {word} 格式的占位符
    PLACEHOLDER_PATTERN = re.compile(r"\{([a-zA-Z0-9_]+)\}")
    # 系统保留占位符，不参与组合生成
    SYSTEM_KEYS = {"modid", "modid_safe"}
    
    def __init__(self, path: Path):
        """初始化模板对象
        
        Args:
            path: 模板文件的 Path 对象
        """
        self.path = path
        self.content = self._load()
        self.placeholders = self._scan()
    
    def _load(self) -> str:
        """读取模板文件内容（自动处理 UTF-8 编码）
        
        Returns:
            模板文件内容的字符串
        """
        return self.path.read_text(encoding="utf-8")
    
    def _scan(self) -> Set[str]:
        """扫描模板中的动态占位符
        
        使用正则表达式找出所有 {xxx}，然后排除系统占位符。
        
        Returns:
            占位符名称集合，如 {"tree", "tool"}
        """
        all_matches = self.PLACEHOLDER_PATTERN.findall(self.content)
        return set(all_matches) - self.SYSTEM_KEYS

class ReplacementEngine:
    """替换引擎：核心逻辑，负责占位符替换
    
    这是一个无状态的纯逻辑类，类似 Java 的 Service 或 Util 类。
    所有方法都是确定性的，给定输入一定有相同输出。
    """
    
    def __init__(self, config: Config):
        """初始化引擎，注入配置对象
        
        Args:
            config: Config 实例，提供命名空间等配置
        """
        self.config = config
    
    def apply(self, content: str, combo: Dict[str, str]) -> str:
        """应用所有替换规则到内容
        
        这是核心方法，按优先级顺序执行：
        1. 解析命名空间
        2. 基础占位符替换
        3. 额外规则替换
        
        Args:
            content: 模板内容字符串
            combo: 当前组合字典，如 {"tree": "oak", "tool": "sword"}
            
        Returns:
            替换完成的内容字符串
        """
        type_info = self._parse_namespaces(combo)
        result = self._apply_basic(content, combo, type_info)
        result = self._apply_extra(result, combo, type_info)
        return result
    
    def _parse_namespaces(self, combo: Dict[str, str]) -> Dict[str, tuple]:
        """解析每个类型的命名空间信息
        
        处理带冒号（带命名空间）和不带冒号（用默认命名空间）的值。
        
        Args:
            combo: 组合字典
            
        Returns:
            类型信息字典: {type: (名称, 完整命名空间, 安全命名空间)}
            例如: {"tree": ("oak", "minecraft:", "")}
        """
        info = {}
        default_ns = self.config.get("default_namespace", "minecraft:")
        
        for r_type, value in combo.items():
            if ":" in value:
                # 带命名空间: "biomesoplenty:bamboo"
                ns, name = value.split(":", 1)
                full_ns, safe_ns = f"{ns}:", f"{ns}_"
            else:
                # 不带命名空间: "oak"
                name = value
                full_ns = default_ns
                safe_ns = "" if full_ns == "minecraft:" else full_ns.replace(":", "_")
            
            info[r_type] = (name, full_ns, safe_ns)
        
        return info
    
    def _apply_basic(self, content: str, combo: Dict, info: Dict) -> str:
        """应用基础占位符替换（{modid}, {modid_safe}, {tree} 等）
        
        Args:
            content: 原始内容
            combo: 组合字典（仅用于获取第一个类型）
            info: 命名空间解析结果
            
        Returns:
            基础替换后的内容
        """
        result = content
        
        # 系统占位符：使用第一个类型的命名空间
        first_type = next(iter(combo.keys()), None)
        modid = info[first_type][1] if first_type in info else self.config.get("default_namespace")
        modid_safe = "" if modid == "minecraft:" else modid.replace(":", "_")
        
        result = result.replace("{modid}", modid).replace("{modid_safe}", modid_safe)
        
        # 类型占位符：{tree} -> oak, {tool} -> sword
        for r_type, (name, _, _) in info.items():
            result = result.replace(f"{{{r_type}}}", name)
        
        return result
    
    def _apply_extra(self, content: str, combo: Dict, info: Dict) -> str:
        """应用额外替换规则（extra 字段中的特定值/通配符替换）
        
        优先级高于基础替换，用于处理特殊情况，
        如 "bamboo" 需要把 "_log" 换成 "_block"。
        
        Args:
            content: 基础替换后的内容
            combo: 组合字典
            info: 命名空间解析结果
            
        Returns:
            最终替换完成的内容
        """
        result = content
        
        for rule in self.config.get_active_rules():
            if rule["type"] not in combo:
                continue
            
            # 获取当前类型的名称（纯名称，不含命名空间）
            name = info[rule["type"]][0]
            extra = rule.get("extra", {})
            
            # 特定值替换：extra["bamboo"]["_log"] = "_block"
            if name in extra:
                for old, new in extra[name].items():
                    result = result.replace(old, new)
            
            # 通配符替换：extra["*"]["_planks"] = "_planks"
            if "*" in extra:
                for old, new in extra["*"].items():
                    result = result.replace(old, new)
        
        return result

class RecipeGenerator:
    """主生成器：协调整个流程
    
    这是 Facade/Controller 类，负责：
    1. 加载配置和模板
    2. 生成所有组合
    3. 调用引擎替换
    4. 写入文件并统计
    
    类似 Java 的 Main 或 Service 类。
    """
    
    def __init__(self, config_path: str):
        """初始化主生成器
        
        Args:
            config_path: 配置文件路径
        """
        self.config = Config(config_path)
        self.engine = ReplacementEngine(self.config)
        self.stats = {"total": 0, "by_type": defaultdict(int)}
    
    def run(self, dry_run: bool = False):
        """运行完整生成流程
        
        Args:
            dry_run: 是否预览模式（不写入文件）
        """
        print("\n🚀 开始生成...\n")
        
        for template_file in self.config.get("template_files", []):
            self._process_template(template_file, dry_run)
        
        self._print_stats()
    
    def _process_template(self, template_file: str, dry_run: bool):
        """处理单个模板文件
        
        Args:
            template_file: 模板文件名，如 "example.json"
            dry_run: 是否预览模式
        """
        template_path = self.config.template_dir / template_file
        
        # 检查文件是否存在
        if not template_path.exists():
            print(f"⚠️  模板不存在: {template_path}")
            return
        
        # 加载模板并生成组合
        template = Template(template_path)
        combos = self._generate_combinations(template.placeholders)
        
        # 遍历每个组合生成文件
        for combo in combos:
            self._generate_file(template, combo, dry_run)
    
    def _generate_combinations(self, needed_types: Set[str]) -> list:
        """为模板生成所有可能的组合（笛卡尔积）
        
        例如：tree=[oak, spruce] × tool=[sword, axe] = 4 个组合
        
        Args:
            needed_types: 模板需要的占位符类型集合
            
        Returns:
            组合列表，每个元素是一个 tuple，如 ("oak", "sword")
        """
        rules = [r for r in self.config.get_active_rules() if r["type"] in needed_types]
        if not rules:
            return []
        
        type_names = [r["type"] for r in rules]
        value_lists = [r["values"] for r in rules]
        
        return list(itertools.product(*value_lists))
    
    def _generate_file(self, template: Template, combo: tuple, dry_run: bool):
        """生成单个文件
        
        Args:
            template: Template 对象
            combo: 当前组合 tuple，如 ("oak", "sword")
            dry_run: 是否预览模式
        """
        # 将 tuple 转换为 dict: {"tree": "oak", "tool": "sword"}
        combo_dict = dict(zip(template.placeholders, combo))
        
        # 应用替换
        content = self.engine.apply(template.content, combo_dict)
        
        # 生成文件名（同样应用替换逻辑）
        name_base = template.path.stem
        filename = self.engine.apply(name_base, combo_dict).replace(":", "_") + ".json"
        
        # 写入文件
        output_path = self.config.output_dir / filename
        
        if dry_run:
            print(f"📄 [预览] {filename}")
            return
        
        output_path.write_text(content, encoding="utf-8")
        self.stats["total"] += 1
        print(f"✏️  {filename}")
    
    def _print_stats(self):
        """打印生成统计信息"""
        print(f"\n=== 🎯 生成完成 ===")
        print(f"总数: {self.stats['total']} 个文件")
