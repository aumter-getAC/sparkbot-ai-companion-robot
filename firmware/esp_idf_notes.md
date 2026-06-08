# ESP-IDF 侧改造要点

## 1. 开发环境

原 sparkbot-45coll README 提到开发环境为 VSCode + ESP-IDF，且 ESP-IDF 版本需 5.3 以上。复现时建议使用 ESP-IDF 5.3.2 或更新的 5.3.x，避免组件版本不一致。

## 2. 需要找的原工程模块

在原始 `code` 工程中优先搜索这些关键词：

```text
openai
chatgpt
api_key
http_client
esp_http_client
websocket
ai
speech
asr
tts
config.h
```

一般改造位置：

- API Key / Base URL / Model：配置文件或 menuconfig；
- 对话请求构造：HTTP POST / WebSocket 发送 JSON 的函数；
- 响应解析：解析 assistant 文本，并送到屏幕显示或 TTS；
- 控制命令：把 AI 返回或本地解析出的动作命令转发给小车控制模块。

## 3. 两种接入方案

### 方案 A：ESP32-S3 直接请求 Qwen API

优点：链路短，不需要额外电脑或服务器。

缺点：API Key 暴露在固件中；HTTPS/TLS、证书、内存占用、长上下文和知识库都更难处理。

### 方案 B：ESP32-S3 请求自建 AI Bridge，再由 Bridge 请求 Qwen API

优点：API Key 安全；知识库、用户画像、日志、模型切换、提示词都在服务端处理；面试更容易讲清楚软件架构。

缺点：需要一台电脑/云服务器/树莓派在同一网络或公网可访问。

本复现仓库推荐方案 B。

## 4. 固件响应链路

```text
唤醒词/触摸进入对话页
→ 麦克风录音/语音识别得到文本
→ HTTP POST 到 AI Bridge
→ 收到 {reply, command}
→ reply：显示到 LCD，并调用 TTS 播放
→ command：若存在，转发给小车底盘或本机功能模块
```
