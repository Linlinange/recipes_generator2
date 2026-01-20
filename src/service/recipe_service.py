
import threading
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable, Union
from src.dao.config_dao import ConfigDAO
from src.dao.template_loader import TemplateLoader
from src.dao.output_writer import OutputWriter
from src.core.engine import ReplacementEngine

class RecipeService:
    """增强版服务：支持异步执行、进度回调、取消操作"""
    
    def __init__(self, 
                 config_path: str,
                 on_progress: Optional[Callable[[str], None]] = None,
                 on_complete: Optional[Callable[[Dict[str, Any]], None]] = None,
                 on_error: Optional[Callable[[Exception], None]] = None):
        # 加载核心依赖
        self.config = ConfigDAO.load(config_path)
        self.engine = ReplacementEngine(
            self.config.default_namespace,
            self.config.rules
        )
        self.template_loader = TemplateLoader(Path(self.config.template_dir))
        self.output_writer = OutputWriter(Path(self.config.output_dir))
        
        # 回调函数（默认为空操作）
        self.on_progress = on_progress or (lambda msg: None)
        self.on_complete = on_complete or (lambda stats: None)
        self.on_error = on_error or (lambda err: None)
        
        # 状态管理
        self._is_running = False
        self._cancel_requested = False
    
    # ==================== 公共API ====================
    
    def run_async(self, dry_run: bool = False, explain_mode: bool = False):
        """异步执行生成任务（立即返回，不阻塞UI）"""
        if self._is_running:
            self.on_progress("⚠️ 任务已在运行中")
            return
        
        self._is_running = True
        self._cancel_requested = False
        
        # 在后台线程执行
        thread = threading.Thread(
            target=self._run_internal,
            args=(dry_run, explain_mode),
            daemon=True
        )
        thread.start()
    
    def cancel(self):
        """请求取消正在运行的任务"""
        self._cancel_requested = True
        self.on_progress("🛑 正在取消任务...")
    
    def is_running(self) -> bool:
        """查询运行状态"""
        return self._is_running
    
    def get_status() -> Dict[str, Union[bool, int, str]]:
        # 返回: 包含 is_running, progress, processed_count, current_template
        # 用途: UI实时显示生成进度
        pass

    # ==================== 内部实现 ====================
    
    def _run_internal(self, dry_run: bool, explain_mode: bool):
        """内部同步执行（在后台线程）"""
        try:
            self.on_progress("\n🚀 开始生成配方...\n")
            
            # 1. 加载模板
            templates = self.template_loader.load_all(self.config.template_files)
            if not templates:
                self.on_progress("⚠️  没有可用的模板，请检查配置。")
                return
            
            self.on_progress(f"📂 加载了 {len(templates)} 个模板")
            
            # 2. 处理每个模板
            for filename, template in templates.items():
                if self._cancel_requested:
                    self.on_progress("\n🛑 任务已取消")
                    break
                
                self._process_template(template, dry_run, explain_mode)
            
            # 3. 完成通知
            if not self._cancel_requested:
                stats = self.output_writer.get_stats()
                self.on_complete(stats)
                if dry_run:
                    self.on_progress("\n⚠️  预览模式，未实际写入文件")
                
        except Exception as e:
            self.on_error(e)
        finally:
            self._is_running = False
    
    def _process_template(self, template, dry_run: bool, explain_mode: bool):
        """处理单个模板"""
        self.on_progress(f"\n📄 处理模板: {template.path.name}")
        
        combos = self.engine.generate_combinations(template)
        if not combos:
            self.on_progress(f"   ⚠️  没有生成任何组合")
            return
        
        self.on_progress(f"   生成 {len(combos)} 个组合")
        
        for combo in combos:
            # 生成文件名
            filename = self.engine.apply(template.path.name, combo, None)
            filename = filename.replace(":", "_")
            
            # 生成内容
            explain_log = [] if explain_mode else None
            content = self.engine.apply(template.content, combo, explain_log)
            
            # 写入文件
            self.output_writer.write(filename, content, dry_run)
            self.on_progress(f"   📄 {'[预览] ' if dry_run else ''}{filename}")
            
            # 解释模式日志
            if explain_log:
                self.on_progress(f"\n   📝 组合详情: {combo}")
                for log in explain_log:
                    self.on_progress(f"      {log}")
