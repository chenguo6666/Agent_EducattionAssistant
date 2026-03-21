import re


def generate_quiz(text: str, count: int = 3) -> list[dict]:
    normalized = re.sub(r"\s+", " ", text).strip()
    points = _extract_points(normalized, max(count, 5))
    if not points:
        points = ["资料的核心内容", "主要观点", "关键事实", "重要结论", "应用场景"]

    quiz_items = []
    for index in range(count):
        point = points[index % len(points)]
        distractors = _build_distractors(point)
        options = [point, *distractors]
        quiz_items.append(
            {
                "question": f"根据材料，下列哪项最符合第 {index + 1} 个核心要点？",
                "options": options,
                "answer": "A",
            }
        )

    return quiz_items


def _extract_points(text: str, limit: int) -> list[str]:
    sentences = re.split(r"[。！？；\n]", text)
    points: list[str] = []
    for sentence in sentences:
        cleaned = sentence.strip(" -:：;；,.，、")
        if len(cleaned) < 8:
            continue
        if cleaned in points:
            continue
        points.append(cleaned[:36])
        if len(points) >= limit:
            break
    return points


def _build_distractors(point: str) -> list[str]:
    return [
        f"与“{point[:10]}”无关的背景信息",
        f"对“{point[:10]}”的错误推论",
        f"与材料结论完全相反的说法",
    ]
