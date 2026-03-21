import re


def summarize_text(text: str) -> str:
    normalized = re.sub(r"\s+", " ", text).strip()
    if not normalized:
        return "未提供可摘要的内容。"

    sentences = [item.strip(" -:：;；,.，、") for item in re.split(r"[。！？；\n]", normalized) if item.strip()]
    useful = [sentence for sentence in sentences if len(sentence) >= 10]
    if not useful:
        return f"核心内容：{normalized[:120]}"

    picked = useful[:3]
    return "核心内容：\n" + "\n".join(f"- {sentence[:80]}" for sentence in picked)
