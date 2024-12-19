import os
from openai import OpenAI
from volcenginesdkarkruntime import Ark

api_keys = {
    "openai": os.getenv("OPENAI_API_KEY", "your_api_key"),
    "doubao": os.getenv("ARK_API_KEY", "your_api_key"),
}

models = {"openai": "gpt-4o", "doubao": "ep-20241216114938-mvdhd"}


def get_client(llm: str):
    """获取llm实例"""
    if llm == "openai":
        client = OpenAI(api_key=api_keys[llm])
    elif llm == "doubao":
        client = Ark(api_key=api_keys[llm])
    else:
        print(f"Unsupported LLM {llm}. Use openai instead")
        client = OpenAI(api_key=api_keys[llm])

    return client
