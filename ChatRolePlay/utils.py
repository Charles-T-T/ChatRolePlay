import tiktoken

enc = tiktoken.get_encoding("cl100k_base")
def count_token(text: str) -> int:
    """计算text对应的token数"""
    tokens = enc.encode(text)
    return len(tokens)
