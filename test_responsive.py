# test_responsive.py
import flet as ft

def main(page: ft.Page):
    """独立测试：弹性布局基础"""
    
    # ========== 窗口设置 ==========
    page.title = "弹性布局测试工具"
    page.window_width = 700
    page.window_height = 500
    page.window_resizable = True      # ✅ 允许拖拽改变窗口大小
    page.window_min_width = 400       # 最小宽度
    page.window_min_height = 300      # 最小高度
    
    # ========== 组件定义 ==========
    
    # 1️⃣ 固定高度的标题栏（不会伸缩）
    header = ft.Container(
        content=ft.Text("🎯 拖拽窗口边缘改变大小", size=24, weight=ft.FontWeight.BOLD, color="white"),
        height=80,                      # 固定80px
        bgcolor=ft.colors.BLUE_600,
        padding=20,
    )
    
    # 2️⃣ 弹性日志区域（占满剩余空间）
    # expand=True 是关键！它会自动填充所有可用空间
    log_area = ft.ListView(
        expand=True,                    # ✅ 弹性填充
        spacing=5,
        padding=10,
    )
    
    # 3️⃣ 固定高度的状态栏
    footer = ft.Container(
        content=ft.Text("准备就绪", size=12),
        height=50,                      # 固定50px
        bgcolor=ft.colors.GREY_900,
        padding=10,
    )
    
    # 4️⃣ 右侧固定宽度的控制面板（可选演示）
    control_panel = ft.Container(
        content=ft.Column([
            ft.Text("控制面板", size=16, weight=ft.FontWeight.BOLD),
            ft.ElevatedButton("添加日志", on_click=lambda e: add_log()),
            ft.ElevatedButton("清空日志", on_click=lambda e: clear_logs()),
        ], spacing=10),
        width=200,                      # 固定200px宽度
        bgcolor=ft.colors.BLUE_GREY_900,
        padding=10,
    )
    
    # ========== 布局组装 ==========
    
    # 主布局：左侧弹性内容 + 右侧固定面板
    main_content = ft.Row(
        [
            # 左侧：标题 + 日志 + 底部状态（Column嵌套）
            ft.Column(
                [
                    header,             # 固定高度80
                    log_area,           # ✅ 弹性填充剩余空间
                    footer,             # 固定高度50
                ],
                expand=True,            # ✅ Column也expand，让它占满Row的剩余宽度
            ),
            
            # 右侧：固定宽度的控制面板
            control_panel,              # 固定宽度200
        ],
        expand=True,                    # ✅ Row也expand，让它占满整个Page
    )
    
    # 添加到页面
    page.add(main_content)
    
    # ========== 交互功能 ==========
    
    def add_log():
        """添加一条日志"""
        log_area.controls.append(
            ft.Text(
                f"日志 #{len(log_area.controls)+1} - 窗口大小 {page.window_width}x{page.window_height}",
                size=14
            )
        )
        page.update()
    
    def clear_logs():
        """清空日志"""
        log_area.controls.clear()
        page.update()
    
    # 初始添加几条日志
    for i in range(5):
        log_area.controls.append(ft.Text(f"初始日志 #{i+1}", size=14))
    
    # ========== 事件监听 ==========
    
    # 监听窗口大小变化，实时更新状态栏
    def on_resize(e):
        footer.content.value = f"窗口大小: {page.window_width} x {page.window_height} 像素"
        page.update()
    
    page.on_resize = on_resize
    
    # 初始调用一次，显示初始尺寸
    on_resize(None)

ft.app(target=main)