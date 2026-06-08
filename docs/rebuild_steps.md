# 复现步骤

## 阶段 1：建立自己的仓库

1. 在 Gitee 或 GitHub 新建仓库，例如：`sparkbot-qwen-assistant`。
2. 本地初始化并推送：

```bash
git init
git add .
git commit -m "init: rebuild sparkbot qwen assistant"
git branch -M main
git remote add origin <你的仓库地址>
git push -u origin main
```

## 阶段 2：拉取参考项目

```bash
git clone https://gitee.com/coll45/sparkbot-45coll.git upstream/sparkbot-45coll
```

建议不要直接在原项目上乱改，而是保留 `upstream/` 作为参考，然后把你自己的改动放到独立目录或新分支。

## 阶段 3：先跑通原工程

1. 安装 VSCode + ESP-IDF 插件；
2. 使用 ESP-IDF 5.3.2 或 5.3 以上版本；
3. 打开原工程 `code` 目录；
4. 根据 README 检查 `config.h` 中 45coll 版本引脚；
5. 先编译原始工程，确认环境可用；
6. 再烧录官方 bin 验证硬件。

## 阶段 4：接入 AI Bridge

1. 启动 `server/ai_bridge.py`；
2. 在电脑浏览器或 curl 中测试 `/chat`；
3. ESP32-S3 固件中新增 HTTP 请求函数；
4. 将原 AI 对话请求入口改为请求 AI Bridge；
5. 解析返回：
   - `reply`：用于屏幕显示和 TTS；
   - `command`：用于小车控制或摄像头控制。

## 阶段 5：知识库与人格化

1. 在 `server/knowledge_base/` 添加 Markdown 文档；
2. 把机器人功能、用户偏好、项目知识、服务话术写进去；
3. 调整 `build_system_prompt()`；
4. 测试不同类型问题：
   - 普通知识问答；
   - 情绪支持；
   - 项目介绍；
   - 小车运动指令；
   - 不知道的问题如何回答。

## 阶段 6：面试展示建议

准备三个演示：

1. **普通问答**：用户问项目/学习问题，机器人自动回答；
2. **知识库问答**：问“你这个项目有什么功能”，回答能体现项目细节；
3. **动作控制**：说“向前走一下/停下/开始巡线”，机器人给出回复并执行命令。
