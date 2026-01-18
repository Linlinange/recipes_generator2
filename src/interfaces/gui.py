import streamlit as st
from pathlib import Path
import json
import sys
import io
from typing import Optional

# 将项目根目录加入 Python 路径
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src import RecipeGenerator

def run_gui():
    """
    Streamlit GUI 主界面
    
    功能：
    - 配置加载/编辑
    - 模板预览
    - 生成控制
    - 实时日志
    - 文件下载
    """
    
    # 页面配置
    st.set_page_config(
        page_title="MC Recipe Generator",
        page_icon="🎮",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # 标题
    st.title("🎮 Minecraft 配方批量生成器")
    st.markdown("配置驱动 · 模板引擎 · 实时预览")
    st.markdown("---")
    
    # 初始化 session state（用于状态管理）
    if "generator" not in st.session_state:
        st.session_state.generator = None
    if "generation_done" not in st.session_state:
        st.session_state.generation_done = False
    
    # 侧边栏：配置和生成控制
    with st.sidebar:
        st.header("⚙️ 生成控制")
        
        # 配置文件路径
        config_path = st.text_input("配置文件路径", value="config.json")
        
        # 检查配置是否存在
        if not Path(config_path).exists():
            st.error("❌ 配置文件不存在")
            st.stop()
        
        st.success("✅ 配置已加载")
        
        # 生成选项
        dry_run = st.checkbox("预览模式（不写入文件）", value=True, key="dry_run")
        explain_mode = st.checkbox("解释模式（详细日志）", key="explain_mode")
        
        st.markdown("---")
        
        # 开始生成按钮
        if st.button("🚀 开始生成", type="primary", use_container_width=True):
            generate(config_path, dry_run, explain_mode)
    
    # 主区域：分栏布局
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # 模板预览
        st.header("📄 模板预览")
        
        template_dir = Path("templates")
        if template_dir.exists():
            template_files = list(template_dir.glob("*.json"))
            if template_files:
                selected_template = st.selectbox(
                    "选择模板",
                    [f.name for f in template_files],
                    key="template_selector"
                )
                
                if selected_template:
                    template_path = template_dir / selected_template
                    template_content = template_path.read_text(encoding="utf-8")
                    st.code(template_content, language="json")
            else:
                st.warning("templates 目录为空")
        else:
            st.error("templates 目录不存在")
    
    with col2:
        # 输出结果
        st.header("📁 输出结果")
        
        output_dir = Path("output")
        if output_dir.exists():
            output_files = list(output_dir.glob("*.json"))
            
            if output_files:
                st.info(f"📊 已生成 {len(output_files)} 个文件")
                
                # 显示最新文件
                latest_files = sorted(output_files, key=lambda x: x.stat().st_mtime, reverse=True)[:10]
                
                for file in latest_files:
                    with st.expander(f"📄 {file.name}"):
                        try:
                            data = json.loads(file.read_text(encoding="utf-8"))
                            st.json(data)
                        except Exception as e:
                            st.error(f"读取失败: {e}")
                
                # 下载按钮
                if st.button("📥 下载所有文件为 ZIP"):
                    download_zip()
            else:
                st.info("暂无输出文件")
        else:
            st.info("输出目录将在首次生成后创建")

def generate(config_path: str, dry_run: bool, explain_mode: bool):
    """
    执行生成任务
    
    捕获所有输出到 Streamlit 界面
    """
    
    # 清空之前的日志
    log_container = st.empty()
    log_lines = []
    
    def log_callback(msg: str):
        """捕获生成器输出到界面"""
        log_lines.append(msg)
        # 只显示最近 30 行，避免界面卡顿
        log_container.text("\n".join(log_lines[-30:]))
    
    # 创建生成器
    try:
        generator = RecipeGenerator(config_path)
    except Exception as e:
        log_callback(f"❌ 配置加载失败: {e}")
        st.error(f"配置加载失败: {e}")
        return
    
    # 重定向 print 到日志
    import builtins
    old_print = builtins.print
    
    def custom_print(*args, **kwargs):
        msg = " ".join(str(arg) for arg in args)
        log_callback(msg)
        old_print(*args, **kwargs)  # 同时打印到控制台
    
    builtins.print = custom_print
    
    # 执行生成
    try:
        with st.spinner("🔄 生成中..."):
            generator.run(dry_run=dry_run, explain_mode=explain_mode)
        
        # 显示完成信息
        total = generator.writer.stats.get("total", 0)
        log_callback(f"\n✅ 生成完成！共 {total} 个文件")
        
        # 刷新输出列表
        st.session_state.generation_done = True
        st.rerun()  # 刷新页面显示新文件
        
    except Exception as e:
        log_callback(f"\n❌ 生成失败: {e}")
        st.error(f"生成失败: {e}")
    
    finally:
        # 恢复原始 print 函数
        builtins.print = old_print

def download_zip():
    """打包输出文件并提供下载"""
    output_dir = Path("output")
    
    if not output_dir.exists():
        st.warning("输出目录不存在")
        return
    
    import zipfile
    from io import BytesIO
    
    # 创建内存中的 zip 文件
    zip_buffer = BytesIO()
    
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for file in output_dir.glob("*.json"):
            zf.write(file, file.name)
    
    zip_buffer.seek(0)
    
    # 提供下载按钮
    st.download_button(
        label="点击下载 recipes.zip",
        data=zip_buffer,
        file_name="recipes.zip",
        mime="application/zip",
        use_container_width=True
    )