
import flet as ft
from pathlib import Path
from typing import Optional
from src.service.recipe_service import RecipeService
from src.dao.config_dao import ConfigDAO

class GeneratorController:
    """生成器控制器：协调UI和RecipeService"""
    
    def __init__(self, page):
        self.page = page
        self._service: Optional[RecipeService] = None
        self._bind_events()
    
    def _bind_events(self):
        """绑定所有事件"""
        # 复选框事件（轻量级日志）
        dry_run = self.page.get_component("dry_run_checkbox")
        if dry_run:
            dry_run.on_change = lambda e: self._log(
                f"ℹ️ 预览模式: {'开' if e.control.value else '关'}"
            )
        
        explain = self.page.get_component("explain_checkbox")
        if explain:
            explain.on_change = lambda e: self._log(
                f"ℹ️ 解释模式: {'开' if e.control.value else '关'}"
            )
        
        # 按钮事件
        gen_btn = self.page.get_component("generate_btn")
        if gen_btn:
            gen_btn.on_click = self._handle_generate
        
        open_btn = self.page.get_component("open_btn")
        if open_btn:
            open_btn.on_click = self._handle_open_dir
    
    def _handle_generate(self, e: ft.ControlEvent):
        """处理生成按钮点击"""
        # 1. 初始化UI状态
        self._init_generation_ui()
        
        # 2. 创建服务实例（带回调）
        self._service = RecipeService(
            config_path=self._get_config_path(),
            on_progress=lambda msg: self._log(msg),
            on_complete=self._on_generation_complete,
            on_error=self._on_generation_error
        )
        
        # 3. 启动异步任务
        dry_run = self.page.get_component("dry_run_checkbox").value
        explain_mode = self.page.get_component("explain_checkbox").value
        self._service.run_async(dry_run=dry_run, explain_mode=explain_mode)
    
    def _init_generation_ui(self):
        """初始化生成UI状态"""
        log_view = self.page.get_component("log_view")
        stats_container = self.page.get_component("stats_container")
        generate_btn = self.page.get_component("generate_btn")
        
        log_view.controls.clear()
        stats_container.content = ft.Text(
            "总数: 0 个文件",
            size=14,
            weight=ft.FontWeight.BOLD
        )
        generate_btn.disabled = True
        generate_btn.text = "生成中..."
        
        self.page.page.update()
    
    def _on_generation_complete(self, stats: dict):
        """生成完成回调"""
        self._log(f"\n✅ 生成完成！总计: {stats['total']} 个文件")
        self._restore_ui(stats)
    
    def _on_generation_error(self, error: Exception):
        """生成错误回调"""
        self._log(f"\n❌ 错误: {error}", color="red", size=14)
        self._restore_ui({"total": 0})
    
    def _restore_ui(self, stats: dict):
        """恢复UI状态"""
        generate_btn = self.page.get_component("generate_btn")
        stats_container = self.page.get_component("stats_container")
        
        generate_btn.disabled = False
        generate_btn.text = "🚀 开始生成"
        generate_btn.update()
        
        stats_container.content = ft.Text(
            f"总数: {stats['total']} 个文件",
            size=14,
            weight=ft.FontWeight.BOLD
        )
        stats_container.update()
    
    def _handle_open_dir(self, e: ft.ControlEvent):
        """打开输出目录"""
        try:
            config = ConfigDAO.load(self._get_config_path())
            output_dir = Path(config.output_dir)
            
            if output_dir.exists():
                import subprocess
                subprocess.Popen(f'explorer "{output_dir.absolute()}"')
                self._log("📂 已打开目录", color="orange")
            else:
                self._log("⚠️ 输出目录不存在", color="orange")
        except Exception as ex:
            self._log(f"❌ 无法打开目录: {ex}", color="red")
    
    def _get_config_path(self) -> str:
        """从UI获取配置路径（默认config.json）"""
        config_field = self.page.get_component("config_field")
        return config_field.value if config_field else "config.json"
    
    def _log(self, message: str, **style):
        """安全的日志输出"""
        log_view = self.page.get_component("log_view")
        if log_view:
            log_view.controls.append(ft.Text(message, size=12, **style))
            log_view.update()