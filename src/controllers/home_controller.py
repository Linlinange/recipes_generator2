
from src.interfaces.home_page import HomePage

class HomeController:
    """首页控制器：仅处理页面导航"""
    
    def __init__(self, router, page: HomePage):
        self.router = router
        self.page = page
        self._bind_events()
    
    def _bind_events(self):
        """绑定导航按钮事件"""
        gen_btn = self.page.get_component("generator_btn")
        if gen_btn:
            gen_btn.on_click = lambda e: self.router.go("generator")
        
        loc_btn = self.page.get_component("localizer_btn")
        if loc_btn:
            loc_btn.on_click = lambda e: self.router.go("localizer")
