# 常见问题排查

## 1. 固件编译失败

- 确认 ESP-IDF 版本 >= 5.3；
- 不要直接用 Arduino IDE 编译 ESP-IDF 工程；
- 检查 Python 虚拟环境和 ESP-IDF 环境变量；
- 如果是组件缺失，先执行 `idf.py reconfigure`。

## 2. Wi-Fi 配不上

- 公开说明中提到不支持 5GHz Wi-Fi，也不支持 5G/2.4G 同名混合网络；
- 使用 2.4GHz 热点测试；
- 确认路由器没有 AP 隔离，否则 ESP32 访问不到电脑 AI Bridge。

## 3. ESP32 请求 AI Bridge 失败

- 电脑防火墙放行 8000 端口；
- ESP32 和电脑在同一个局域网；
- `AI_BRIDGE_URL` 不要写 `127.0.0.1`，要写电脑局域网 IP；
- 用手机浏览器访问 `http://电脑IP:8000/health` 先验证网络。

## 4. Qwen API 报 401 / 403

- API Key 未配置或复制错误；
- DashScope 服务未开通；
- base_url 写错；
- 国内和国际 endpoint 不要混用。

## 5. 回复太慢

- 限制 `max_tokens`；
- 缩短 prompt 和历史对话；
- 减少知识库片段数量；
- 先返回“我正在想一下”，再异步播报完整答案；
- 换更快的模型，例如 turbo 类模型。

## 6. 回复不适合语音播报

- system prompt 中明确要求短句、口语化、少列表、少 Markdown；
- 对回复做后处理，去掉标题、代码块和表格；
- 情绪支持场景避免长篇说教。

## 7. 大模型乱控制机器人

- 不让模型直接输出底层电机参数；
- 只允许有限动作集合：forward/backward/turn_left/turn_right/stop/line_tracking/capture；
- 固件侧再做安全检查，例如速度上限、超时自动停止。
