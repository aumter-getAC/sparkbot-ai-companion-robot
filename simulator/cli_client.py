"""
电脑端模拟 SparkBot 输入输出。

用途：没有 ESP32 硬件时，用命令行模拟：
用户输入文本 -> 请求 AI Bridge /chat -> 打印机器人回复和动作命令。

启动前：
1. cd server && uvicorn ai_bridge:app --host 127.0.0.1 --port 8000
2. 另开终端：python simulator/cli_client.py
"""
from __future__ import annotations

import json
import urllib.error
import urllib.request

BRIDGE_URL = "http://127.0.0.1:8000/chat"


def post_chat(message: str, history: list[dict[str, str]]) -> dict:
    payload = {
        "user_id": "laptop_demo",
        "message": message,
        "mode": "companion",
        "history": history[-6:],
    }
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        BRIDGE_URL,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main() -> None:
    print("SparkBot laptop simulator. 输入 exit 退出。")
    history: list[dict[str, str]] = []
    while True:
        user_text = input("\n你：").strip()
        if user_text.lower() in {"exit", "quit", "q"}:
            break
        if not user_text:
            continue
        try:
            result = post_chat(user_text, history)
        except urllib.error.URLError as e:
            print("请求 AI Bridge 失败：", e)
            print("请先启动 server/ai_bridge.py，并检查 8000 端口。")
            continue
        reply = result.get("reply", "")
        command = result.get("command")
        print("机器人：", reply)
        if command:
            print("模拟动作命令：", json.dumps(command, ensure_ascii=False))
        history.append({"role": "user", "content": user_text})
        history.append({"role": "assistant", "content": reply})


if __name__ == "__main__":
    main()
