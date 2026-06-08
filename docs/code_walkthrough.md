# 核心代码逐段讲解

## 1. server/ai_bridge.py 是什么

它是“机器人 AI 中间层”。没有它时，ESP32 要自己处理 API Key、HTTPS、知识库、上下文、模型切换和 JSON 解析；有了它以后，ESP32 只需要把用户文本发给 `/chat`，再接收：

```json
{
  "reply": "机器人要说的话",
  "command": {"type": "move", "action": "forward", "speed": 0.5},
  "retrieved_context": ["检索到的知识片段"]
}
```

## 2. 配置区

```python
load_dotenv()
BASE_DIR = Path(__file__).resolve().parent
KB_DIR = BASE_DIR / "knowledge_base"
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "")
QWEN_BASE_URL = os.getenv("QWEN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
QWEN_MODEL = os.getenv("QWEN_MODEL", "qwen-plus")
ROBOT_NAME = os.getenv("ROBOT_NAME", "小智")
```

含义：从 `.env` 读取 API Key、模型地址、模型名和机器人名字。API Key 不写死在代码里，是为了避免上传仓库泄露。

## 3. 请求和响应数据结构

```python
class ChatRequest(BaseModel):
    user_id: str = Field(default="default")
    message: str
    mode: str = Field(default="companion")
    history: List[Dict[str, str]] = Field(default_factory=list)
```

这表示 ESP32 或电脑模拟器请求 `/chat` 时，需要传入用户消息。`history` 用于多轮对话，但只保留最近几轮，避免上下文太长。

```python
class ChatResponse(BaseModel):
    reply: str
    command: Optional[Dict[str, Any]] = None
    retrieved_context: List[str] = Field(default_factory=list)
```

这表示服务端返回三类信息：机器人说的话、可选动作命令、检索到的知识库片段。

## 4. load_knowledge_base()

```python
def load_knowledge_base() -> List[str]:
    chunks = []
    for path in KB_DIR.glob("*.md"):
        text = path.read_text(encoding="utf-8", errors="ignore")
        for block in re.split(r"\n(?=# )|\n(?=## )|\n\s*\n", text):
            block = block.strip()
            if len(block) > 20:
                chunks.append(block[:1200])
    return chunks
```

作用：读取 `server/knowledge_base/` 里面所有 Markdown 文件，并按标题或空行切成片段。`block[:1200]` 是为了限制单个片段长度，避免 prompt 过长。

## 5. retrieve_context()

```python
def retrieve_context(query: str, top_k: int = 3) -> List[str]:
    query_terms = set(re.findall(r"[\w\u4e00-\u9fff]+", query.lower()))
    scored = []
    for chunk in load_knowledge_base():
        chunk_terms = set(re.findall(r"[\w\u4e00-\u9fff]+", chunk.lower()))
        score = len(query_terms & chunk_terms)
        if score > 0:
            scored.append((score, chunk))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [chunk for _, chunk in scored[:top_k]]
```

这是轻量关键词检索：把用户问题和知识库片段都切成词，计算交集数量，分数高的片段放进 prompt。

它不是高级 RAG，但适合面试演示。升级版可以换成：embedding 模型 + FAISS/Chroma/Milvus 向量数据库。

## 6. detect_robot_command()

```python
rules = [
    (r"前进|向前|往前", {"type": "move", "action": "forward", "speed": 0.5}),
    (r"停止|停下|别动", {"type": "move", "action": "stop", "speed": 0}),
]
```

作用：把自然语言变成结构化动作命令。比如用户说“向前走一下”，服务端返回：

```json
{"type": "move", "action": "forward", "speed": 0.5}
```

真实硬件上，ESP32-S3 收到这个 JSON 后，把 `forward` 转成底盘控制命令发给 ESP32-C3。

## 7. build_system_prompt()

这个函数决定机器人“像谁、能干什么、不能干什么”：

- 你是小智；
- 你运行在 ESP32-S3 桌面机器人上；
- 回答要简短，适合语音播报；
- 情绪低落时先共情再建议；
- 不要假装看到用户；
- 项目介绍时突出 ESP32-S3、ESP32-C3、Qwen、知识库、动作控制闭环。

面试里可以说：

> 我通过 system prompt 约束模型人格、回答长度、情绪支持方式和硬件动作边界，使通用大模型更适合桌面机器人场景。

## 8. call_qwen()

```python
client = OpenAI(api_key=DASHSCOPE_API_KEY, base_url=QWEN_BASE_URL)
completion = client.chat.completions.create(
    model=QWEN_MODEL,
    messages=messages,
    temperature=0.7,
    max_tokens=600,
)
```

Qwen 提供 OpenAI-compatible API，因此可以用 OpenAI SDK 调用。核心就是换 `base_url`、`api_key`、`model`。`temperature` 控制生成随机性，`max_tokens` 限制回复长度。

## 9. chat() 主流程

```python
@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    user_text = req.message.strip()
    contexts = retrieve_context(user_text)
    command = detect_robot_command(user_text)
    messages = [{"role": "system", "content": build_system_prompt(req.mode, contexts)}]
    for item in req.history[-6:]:
        ...
    messages.append({"role": "user", "content": user_text})
    reply = call_qwen(messages)
    return ChatResponse(reply=reply, command=command, retrieved_context=contexts)
```

完整链路：

```text
检查用户输入
→ 检索知识库
→ 判断是否有动作命令
→ 构造 system/user/history messages
→ 调 Qwen
→ 返回 reply + command
```

## 10. firmware/qwen_bridge_client_example.c

这个文件不是完整固件，是移植示例。核心函数：

```c
esp_err_t sparkbot_send_text_to_ai_bridge(const char *user_text)
```

作用：ESP32 把 ASR 得到的 `user_text` 打包成 JSON：

```json
{"user_id":"sparkbot","message":"你好","mode":"companion"}
```

然后用 `esp_http_client_perform()` POST 到 AI Bridge。收到响应后，真实项目里需要补充：读取 body、用 cJSON 解析 `reply` 和 `command`，再送给 LCD/TTS/小车控制模块。

## 11. simulator/cli_client.py

这是无硬件替代方案。它做了 ESP32 的“软件模拟”：

```text
命令行输入文本 = 语音识别后的文字
打印 reply = 屏幕显示/TTS 播报
打印 command = 小车动作执行
```

因此你没有硬件也能展示软件链路。
