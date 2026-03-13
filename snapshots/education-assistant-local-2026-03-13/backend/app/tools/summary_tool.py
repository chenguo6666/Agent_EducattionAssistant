def summarize_text(text: str) -> str:
    normalized = " ".join(text.split())
    if not normalized:
        return "未提供可摘要的内容。"

    if len(normalized) <= 120:
        return f"核心内容：{normalized}"

    return f"核心内容：{normalized[:120]}..."
