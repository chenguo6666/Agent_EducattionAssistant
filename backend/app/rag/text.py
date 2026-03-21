from __future__ import annotations

import re


def tokenize_text(text: str) -> list[str]:
    normalized = " ".join(text.split())
    chinese_sequences = re.findall(r"[\u4e00-\u9fff]{2,}", normalized)
    english_terms = re.findall(r"[A-Za-z][A-Za-z0-9_-]{2,}", normalized.lower())

    tokens: list[str] = []
    for sequence in chinese_sequences:
        for index in range(len(sequence) - 1):
            token = sequence[index : index + 2]
            if token not in tokens:
                tokens.append(token)
        if sequence not in tokens:
            tokens.append(sequence)

    for term in english_terms:
        if term not in tokens:
            tokens.append(term)

    return tokens[:40]


def chunk_text(text: str, chunk_size: int = 900, overlap: int = 120, max_chunks: int = 30) -> list[str]:
    normalized = " ".join(text.replace("\r", "\n").split())
    if not normalized:
        return []

    chunks: list[str] = []
    start = 0
    separators = ["。", "！", "？", "\n", ".", ";", "；", ",", "，", " "]
    while start < len(normalized):
        end = min(start + chunk_size, len(normalized))
        if end < len(normalized):
            split_at = -1
            for separator in separators:
                candidate = normalized.rfind(separator, start, end)
                if candidate > start + chunk_size // 2:
                    split_at = max(split_at, candidate + len(separator))
            if split_at > start:
                end = split_at
        chunk = normalized[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(normalized):
            break
        start = max(end - overlap, start + 1)

    return chunks[:max_chunks]
