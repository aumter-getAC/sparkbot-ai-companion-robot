# 没有 ESP 硬件时怎么展示项目

## 1. 结论

不影响软件侧复现与面试展示。你可以把项目从“实体机器人完整复刻”调整为“机器人 AI 软件链路复现与桌面端模拟”。

你现在能真实完成并展示的内容：

1. Qwen API 调用；
2. 角色 Prompt 调校；
3. 知识库检索/RAG 雏形；
4. 自然语言动作命令解析；
5. AI Bridge 服务；
6. 电脑端模拟 ESP32 请求与机器人输出；
7. 微调数据集和 LoRA 训练实验。

你现在不能真实证明的内容：

1. ESP32-S3 上的真实语音输入；
2. LCD/TTS/摄像头真实运行；
3. ESP32-C3 小车真实运动；
4. Wi-Fi 配网和硬件串口/底盘通信。

面试时建议说：

> 由于目前没有硬件，我保留了原项目的硬件链路说明，并在电脑端复现了大模型服务层、知识库、指令解析和机器人交互协议。硬件侧可以通过相同 HTTP/JSON 接口接入，等价于把 ESP32 输入输出用电脑模拟。

## 2. 电脑端演示路径

```text
命令行输入用户问题
→ simulator/cli_client.py
→ server/ai_bridge.py
→ Qwen API
→ 返回 reply + command
→ 命令行打印“机器人回复”和“模拟动作命令”
```

离线演示：

```bash
python simulator/offline_logic_demo.py
```

联网演示：

```bash
cd server
uvicorn ai_bridge:app --host 127.0.0.1 --port 8000
# 另开终端
python simulator/cli_client.py
```
