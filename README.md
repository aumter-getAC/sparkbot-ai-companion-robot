# SparkBot-Qwen 桌面陪伴机器人复现仓库

SparkBot 接入 Qwen API，改造成具备知识库、桌面陪伴、情感支持和服务能力的机器人

## 1. 项目定位

硬件平台：ESP-SparkBot / sparkbot-45coll。



 ESP32-S3 桌面机器人上完成语音唤醒、用户输入、联网请求、AI 回复、屏幕/语音输出闭环；

通过系统提示词 + 本地知识库检索 + 用户画像，让机器人具备“个人化桌面助手”能力；
保留机器人场景能力，例如天气、网页控制、小车运动、巡线、摄像头、AI 对话控制小车等。

## 2. 架构

```text
用户语音/触摸/网页输入
        ↓
ESP32-S3 SparkBot 头部主控
        ↓ Wi-Fi / HTTP / WebSocket
AI Bridge 服务（Python，可部署在电脑/云服务器/树莓派）
        ↓
Qwen API + 知识库检索 + 机器人角色提示词 + 指令解析
        ↓
回复文本 + 可选机器人控制命令
        ↓
ESP32-S3 显示/播报，并向 ESP32-C3 小车发送控制指令
```

## 3. 目录说明

```text
server/                    AI Bridge 服务端
  ai_bridge.py             FastAPI 服务：Qwen 调用、知识库检索、情感支持、命令识别
  requirements.txt         Python 依赖
  .env.example             API Key 与模型配置示例
  knowledge_base/          个人知识库 Markdown 示例
firmware/                  ESP-IDF 侧接入示例和配置说明
hardware/                  硬件复现注意事项
docs/                      面试讲解、复现步骤、问题排查
scripts/                   创建远程仓库和推送命令
```

## 4. 快速启动 AI Bridge

```bash
cd server
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
cp .env.example .env
# 修改 .env，填入 DASHSCOPE_API_KEY
uvicorn ai_bridge:app --host 0.0.0.0 --port 8000
```

测试：

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id":"demo","message":"你好，你是谁？"}'
```

