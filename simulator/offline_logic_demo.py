"""
不调用 Qwen API 的离线逻辑演示。

用途：没有 API Key、没有硬件时，也能展示：
1. 知识库检索；
2. 自然语言动作意图解析；
3. 给面试老师说明“硬件收到 command 后如何执行”。
"""
from pathlib import Path
import re
import json

KB_DIR = Path(__file__).resolve().parents[1] / "server" / "knowledge_base"


def load_knowledge_base() -> list[str]:
    chunks: list[str] = []
    for path in KB_DIR.glob("*.md"):
        text = path.read_text(encoding="utf-8", errors="ignore")
        for block in re.split(r"\n(?=# )|\n(?=## )|\n\s*\n", text):
            block = block.strip()
            if len(block) > 20:
                chunks.append(block[:1200])
    return chunks


def retrieve_context(query: str, top_k: int = 3) -> list[str]:
    query_terms = set(re.findall(r"[\w\u4e00-\u9fff]+", query.lower()))
    scored: list[tuple[int, str]] = []
    for chunk in load_knowledge_base():
        chunk_terms = set(re.findall(r"[\w\u4e00-\u9fff]+", chunk.lower()))
        score = len(query_terms & chunk_terms)
        if score > 0:
            scored.append((score, chunk))
    return [chunk for _, chunk in sorted(scored, reverse=True)[:top_k]]


def detect_robot_command(text: str) -> dict | None:
    rules = [
        (r"前进|向前|往前", {"type": "move", "action": "forward", "speed": 0.5}),
        (r"后退|倒退", {"type": "move", "action": "backward", "speed": 0.4}),
        (r"左转|向左", {"type": "move", "action": "turn_left", "speed": 0.35}),
        (r"右转|向右", {"type": "move", "action": "turn_right", "speed": 0.35}),
        (r"停止|停下|别动", {"type": "move", "action": "stop", "speed": 0}),
        (r"巡线|循迹", {"type": "mode", "action": "line_tracking"}),
        (r"拍照|拍一张", {"type": "camera", "action": "capture"}),
    ]
    for pattern, command in rules:
        if re.search(pattern, text):
            return command
    return None


if __name__ == "__main__":
    samples = [
        "介绍一下你这个机器人项目", 
        "我今天有点焦虑，陪我说两句", 
        "向前走一下然后停下", 
        "开始巡线",
    ]
    for s in samples:
        print("\n用户问题：", s)
        print("检索片段：", retrieve_context(s))
        print("动作命令：", json.dumps(detect_robot_command(s), ensure_ascii=False))
