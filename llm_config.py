# llm_config.py
import json
import os
from typing import Dict, List, Optional

# LLM配置文件路径
LLM_CONFIG_FILE = "llm_config.json"

# 默认LLM配置
DEFAULT_LLM_CONFIG = {
    "api_keys": {
        "kimi": "",
        "openai": "",
        "gemini": ""
    },
    "base_urls": {
        "kimi": "https://api.moonshot.cn/v1",
        "openai": "https://api.gptsapi.net/v1",
        "gemini": ""
    },
    "models": {
        "kimi": [
            {"id": "kimi-k2-turbo-preview", "name": "Kimi K2 Turbo", "provider": "kimi"},
            {"id": "moonshot-v1-8k", "name": "Moonshot V1 8K", "provider": "kimi"},
            {"id": "moonshot-v1-32k", "name": "Moonshot V1 32K", "provider": "kimi"}
        ],
        "openai": [
            {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "provider": "openai"},
            {"id": "gpt-4", "name": "GPT-4", "provider": "openai"},
            {"id": "gpt-4-turbo", "name": "GPT-4 Turbo", "provider": "openai"},
            {"id": "gpt-4o", "name": "GPT-4o", "provider": "openai"}
        ],
        "gemini": [
            {"id": "gemini-1.5-flash", "name": "Gemini 1.5 Flash", "provider": "gemini"},
            {"id": "gemini-1.5-pro", "name": "Gemini 1.5 Pro", "provider": "gemini"},
            {"id": "gemini-2.5-flash", "name": "Gemini 2.5 Flash", "provider": "gemini"}
        ]
    },
    "selected_model": "kimi-k2-turbo-preview",
    "temperature": 0.7,
    "max_tokens": 60000
}

def load_llm_config() -> Dict:
    """加载LLM配置"""
    if os.path.exists(LLM_CONFIG_FILE):
        try:
            with open(LLM_CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                # 确保所有必要的键都存在
                for key in DEFAULT_LLM_CONFIG:
                    if key not in config:
                        config[key] = DEFAULT_LLM_CONFIG[key]
                return config
        except Exception as e:
            print(f"加载LLM配置失败: {e}")
    
    return DEFAULT_LLM_CONFIG.copy()

def save_llm_config(config: Dict) -> bool:
    """保存LLM配置"""
    try:
        with open(LLM_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"保存LLM配置失败: {e}")
        return False

def get_available_models() -> List[Dict]:
    """获取所有可用模型"""
    config = load_llm_config()
    models = []
    
    for provider, model_list in config["models"].items():
        for model in model_list:
            models.append(model)
    
    return models

def get_model_info(model_id: str) -> Optional[Dict]:
    """根据模型ID获取模型信息"""
    models = get_available_models()
    for model in models:
        if model["id"] == model_id:
            return model
    return None

def get_provider_config(provider: str) -> Dict:
    """获取提供商配置"""
    config = load_llm_config()
    return {
        "api_key": config["api_keys"].get(provider, ""),
        "base_url": config["base_urls"].get(provider, "")
    }
