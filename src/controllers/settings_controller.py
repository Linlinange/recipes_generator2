
import json
import flet as ft
from pathlib import Path
from typing import Optional

class SettingsController:
    """设置页控制器：处理配置持久化"""
    
    def __init__(self, page):
        self.page = page
        self._original_btn_style: Optional[dict] = None
        self._save_btn_animation_task = None
        self._bind_events()
    
    def _bind_events(self):
        """绑定事件"""
        # 绑定保存按钮
        save_btn = self.page.get_component("save_btn")
        if save_btn:
            save_btn.on_click = self._save_config
        
        # 其他字段变更事件由SettingsPage内部处理（已存在）
        # 这里不再需要重复绑定
    def _save_config(self, e: ft.ControlEvent):
        """保存配置文件"""
        try:
            save_btn = self.page.get_component("save_btn")
            if not save_btn:
                return
            
            # 调用SettingsPage的save_config方法
            if self.page.save_config():
                self._show_save_success(save_btn)
            else:
                self._log("❌ 保存失败", color="red")
        except Exception as ex:
            self._log(f"❌ 保存失败: {ex}", color="red")
    
    def _show_save_success(self, btn: ft.ElevatedButton):
        """显示保存成功动画"""
        # 取消之前可能的动画任务
        if self._save_btn_animation_task:
            self._save_btn_animation_task.cancel()
        
        # 保存原始样式
        if not self._original_btn_style:
            self._original_btn_style = {
                "text": btn.text,
                "bgcolor": btn.bgcolor,
                "color": btn.color
            }
        
        # 更新为成功样式
        btn.text = "✅ 保存成功"
        btn.bgcolor = ft.colors.GREEN
        btn.update()
        
        # 3秒后恢复
        def restore():
            try:
                btn.text = self._original_btn_style["text"]
                btn.bgcolor = self._original_btn_style["bgcolor"]
                btn.update()
            except Exception:
                pass  # 页面可能已关闭
        
        self._save_btn_animation_task = self.page.page.run_task(restore, delay=3)
    
    def _log(self, message: str, **style):
        """极简日志（Settings页不显示复杂日志）"""
        print(f"Settings: {message}")