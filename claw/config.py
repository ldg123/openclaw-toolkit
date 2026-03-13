"""
配置管理模块
"""

import json
import os
from typing import Dict, Any, Optional
from pathlib import Path


DEFAULT_CONFIG = {
    "serial": {
        "baudrate": 115200,
        "timeout": 1.0,
        "bytesize": 8,
        "parity": "N",
        "stopbits": 1
    },
    "claw": {
        "angle_min": 0,
        "angle_max": 180,
        "angle_default": 90,
        "grip_angle": 45
    },
    "gui": {
        "window_width": 800,
        "window_height": 600,
        "theme": "light",
        "log_max_lines": 1000,
        "auto_connect": False
    },
    "general": {
        "language": "zh_CN",
        "log_level": "INFO"
    }
}


class Config:
    """配置管理类"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化配置
        
        Args:
            config_path: 配置文件路径，默认 ~/.openclaw-toolkit/config.json
        """
        if config_path:
            self.config_path = Path(config_path)
        else:
            self.config_path = self._get_default_config_path()
            
        self.config = self._load()
        
    def _get_default_config_path(self) -> Path:
        """获取默认配置路径"""
        home = Path.home()
        config_dir = home / ".openclaw-toolkit"
        config_dir.mkdir(exist_ok=True)
        return config_dir / "config.json"
        
    def _load(self) -> Dict[str, Any]:
        """加载配置"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                return self._merge_config(DEFAULT_CONFIG, user_config)
            except Exception:
                pass
        return DEFAULT_CONFIG.copy()
        
    def _merge_config(self, default: Dict, user: Dict) -> Dict:
        """合并配置"""
        result = default.copy()
        for key, value in user.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_config(result[key], value)
            else:
                result[key] = value
        return result
        
    def save(self) -> None:
        """保存配置"""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=4, ensure_ascii=False)
            
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            key: 配置键，支持点号分隔，如 "serial.baudrate"
            default: 默认值
            
        Returns:
            配置值
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
                
        return value
        
    def set(self, key: str, value: Any) -> None:
        """
        设置配置值
        
        Args:
            key: 配置键，支持点号分隔
            value: 配置值
        """
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
            
        config[keys[-1]] = value
        
    def reset(self) -> None:
        """重置为默认配置"""
        self.config = DEFAULT_CONFIG.copy()
        self.save()


# 全局配置实例
_config: Optional[Config] = None


def get_config() -> Config:
    """获取全局配置实例"""
    global _config
    if _config is None:
        _config = Config()
    return _config


def init_config(config_path: Optional[str] = None) -> Config:
    """初始化配置"""
    global _config
    _config = Config(config_path)
    return _config
