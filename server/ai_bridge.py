"""
SparkBot-Qwen AI Bridge

作用：
1. 接收 ESP32-S3 / 网页端发来的用户文本；
2. 读取本地知识库，做轻量检索；
3. 调用 Qwen OpenAI-compatible Chat Completions API；
4. 返回机器人可播报文本，以及可选运动控制命令。

注意：这是复现工程骨架，真实部署时可继续加入：
- 语音识别 STT / 语音合成 TTS；
- 向量数据库与 embedding 检索；
- 多轮会话持久化；
- 更严格的 JSON function calling；
- 鉴权、限流和日志脱敏。
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from openai import OpenAI
from pydantic import BaseModel, Field

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
KB_DIR = BASE_DIR / "knowledge_base"

DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "")
QWEN_BASE_URL = os.getenv("QWEN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
QWEN_MODEL = os.getenv("QWEN_MODEL", "qwen-plus")
ROBOT_NAME = os.getenv("ROBOT_NAME", "小智")

app = FastAPI(title="SparkBot-Qwen AI Bridge", version="0.1.0")


class ChatRequest(BaseModel):
    user_id: str = Field(default="default")
    message: str
    mode: str = Field(default="companion", description="companion / qa / robot_control")
    history: List[Dict[str, str]] = Field(default_factory=list)


class ChatResponse(BaseModel):
    reply: str
    command: Optional[Dict[str, Any]] = None
    retrieved_context: List[str] = Field(default_factory=list)


def load_knowledge_base() -> List[str]:
    chunks: List[str] = []
    if not KB_DIR.exists():
        return chunks
    for path in KB_DIR.glob("*.md"):
        text = path.read_text(encoding="utf-8", errors="ignore")
        for block in re.split(r"\n(?=# )|\n(?=## )|\n\s*\n", text):
            block = block.strip()
            if len(block) > 20:
                chunks.append(block[:1200])
    return chunks


def retrieve_context(query: str, top_k: int = 3) -> List[str]:
    """轻量关键词检索。面试时可说明后续可升级为 embedding + 向量数据库。"""
    query_terms = set(re.findall(r"[\w\u4e00-\u9fff]+", query.lower()))
    scored: List[tuple[int, str]] = []
    for chunk in load_knowledge_base():
        chunk_terms = set(re.findall(r"[\w\u4e00-\u9fff]+", chunk.lower()))
        score = len(query_terms & chunk_terms)
        if score > 0:
            scored.append((score, chunk))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [chunk for _, chunk in scored[:top_k]]


def detect_robot_command(text: str) -> Optional[Dict[str, Any]]:
    """把自然语言中的简单运动意图转成机器人底盘命令。"""
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


def build_system_prompt(mode: str, contexts: List[str]) -> str:
    context_text = "\n\n".join(f"[知识片段{i+1}]\n{c}" for i, c in enumerate(contexts))
    return f"""
你是{ROBOT_NAME}，一个运行在 ESP32-S3 桌面机器人上的中文 AI 助手。
你的任务：自动回答用户问题、提供情感支持、根据用户需要给出服务建议，并在需要时配合机器人硬件执行简单动作。

行为要求：
1. 回答要简洁、自然、适合通过小机器人语音播报。
2. 用户情绪低落时，先共情，再给出一个很小、可马上执行的建议。
3. 不要假装自己真的看见用户，除非系统明确提供摄像头识别结果。
4. 涉及机器人运动时，先用一句话确认动作意图，不输出危险动作。
5. 对项目介绍问题，突出：ESP32-S3、ESP32-C3、Wi-Fi 通信、Qwen API、知识库检索、提示词人格化、语音/屏幕/小车控制闭环。

当前模式：{mode}

可用知识库：
{context_text if context_text else "暂无额外知识库。"}
""".strip()


def call_qwen(messages: List[Dict[str, str]]) -> str:
    if not DASHSCOPE_API_KEY or DASHSCOPE_API_KEY == "your_dashscope_api_key_here":
        raise HTTPException(status_code=500, detail="DASHSCOPE_API_KEY 未配置。请在 server/.env 中填写 API Key。")

    client = OpenAI(api_key=DASHSCOPE_API_KEY, base_url=QWEN_BASE_URL)
    completion = client.chat.completions.create(
        model=QWEN_MODEL,
        messages=messages,
        temperature=0.7,
        max_tokens=600,
    )
    return completion.choices[0].message.content or ""


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok", "model": QWEN_MODEL, "base_url": QWEN_BASE_URL}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    user_text = req.message.strip()
    if not user_text:
        raise HTTPException(status_code=400, detail="message 不能为空")

    contexts = retrieve_context(user_text)
    command = detect_robot_command(user_text)

    messages: List[Dict[str, str]] = [
        {"role": "system", "content": build_system_prompt(req.mode, contexts)}
    ]

    # 仅保留最近几轮，避免 ESP32/服务端请求过大。
    for item in req.history[-6:]:
        role = item.get("role")
        content = item.get("content")
        if role in {"user", "assistant"} and content:
            messages.append({"role": role, "content": content})

    messages.append({"role": "user", "content": user_text})

    reply = call_qwen(messages)

    return ChatResponse(reply=reply, command=command, retrieved_context=contexts)
