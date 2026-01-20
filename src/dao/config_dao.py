
import json
from pathlib import Path
from src.model.config import Config

class ConfigDAO:
    """配置数据访问对象：负责加载JSON配置并返回Config模型"""
    
    @staticmethod
    def load(path: str) -> Config:
        """从文件加载配置，自动迁移旧格式"""
        config_path = Path(path)
        if not config_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {path}")
        
        with config_path.open("r", encoding="utf-8") as f:
            raw_data = json.load(f)
        
        # 复用Config的from_dict方法，统一旧格式迁移逻辑
        return Config.from_dict(raw_data)
    
    @staticmethod
    def save(config: Config, path: str = "config.json") -> bool:
        """
        将Config对象保存为JSON配置文件
        
        参数:
            config: Config对象
            path: 保存路径（默认config.json）
        
        返回:
            成功返回True，失败返回False
        
        备注: 处理文件写入异常、JSON序列化错误，保证编码为UTF-8
        """
        try:
            # 复用Config的to_dict方法，统一序列化逻辑
            config_dict = config.to_dict()
            
            # 确保配置文件父目录存在
            config_path = Path(path)
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 写入JSON文件（格式化输出，保证中文正常显示）
            with config_path.open("w", encoding="utf-8") as f:
                json.dump(config_dict, f, ensure_ascii=False, indent=4)
            
            return True
        except (IOError, json.JSONEncodeError) as e:
            # 捕获常见的文件操作/序列化异常
            print(f"保存配置文件失败: {str(e)}")
            return False
        except Exception as e:
            # 兜底捕获未预期的异常
            print(f"保存配置文件时发生未预期错误: {str(e)}")
            return False
