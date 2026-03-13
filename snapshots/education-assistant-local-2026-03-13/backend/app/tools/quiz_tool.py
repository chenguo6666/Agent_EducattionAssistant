def generate_quiz(text: str, count: int = 3) -> list[dict]:
    base = " ".join(text.split()) or "学习材料"
    quiz_items = []

    for index in range(count):
        quiz_items.append(
            {
                "question": f"根据材料，下列哪项最符合第 {index + 1} 个知识点？",
                "options": [
                    f"{base[:16]} 的核心概念",
                    "无关背景信息",
                    "错误推论",
                    "完全相反的结论",
                ],
                "answer": "A",
            }
        )

    return quiz_items
