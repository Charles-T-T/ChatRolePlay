import os
from openai import OpenAI
from volcenginesdkarkruntime import Ark

# 定义支持的 LLM 提供商及其模型
LLM_PROVIDERS = {
    "openai": {
        "api_key": os.getenv("OPENAI_API_KEY", "your_api_key"),
        "models": [
            "gpt-3.5-turbo",
            "gpt-4o-mini",
            "gpt-4o",
            "o1",
            "o3-mini",
        ],
    },
    "doubao": {
        "api_key": os.getenv("ARK_API_KEY", "your_api_key"),
        "models": [
            "ep-20241214144520-56skd",  # Doubao-vision-lite-32k
            "ep-20250206211623-dc6g2",  # Doubao-1.5-pro-32k-250115
        ],
    },
    "deepseek": {
        "api_key": os.getenv("DEEPSEEK_API_KEY", "your_api_key"),
        "models": ["deepseek-chat", "deepseek-reasoner"],
    },
}


def get_client(model: str):
    """获取LLM实例

    Args:
        model (str): 模型名称

    Raises:
        ValueError: 错误/尚未支持的模型名称

    Returns:
        LLM实例
    """

    for provider, details in LLM_PROVIDERS.items():
        if model in details["models"]:
            api_key = details["api_key"]

            if provider == "openai":
                return OpenAI(api_key=api_key)
            elif provider == "doubao":
                return Ark(api_key=api_key)
            elif provider == "deepseek":
                return OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

    raise ValueError(
        f"Unsupported LLM model: {model}. Please check the model name."
    )
