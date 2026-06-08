# 创建你自己的仓库并推送

## 方案 A：Gitee 网页创建

1. 登录 Gitee；
2. 点击“新建仓库”；
3. 仓库名建议：`sparkbot-qwen-assistant` 或 `sparkbot-ai-rebuild`；
4. 可见性：面试展示建议公开；如果包含 API Key，必须私有或删除 Key；
5. 不要勾选自动生成 README，避免和本地冲突。

本地执行：

```bash
cd sparkbot-qwen-rebuild
git init
git add .
git commit -m "init: rebuild sparkbot qwen assistant"
git branch -M main
git remote add origin https://gitee.com/<你的用户名>/sparkbot-qwen-assistant.git
git push -u origin main
```

## 方案 B：GitHub 网页创建

```bash
cd sparkbot-qwen-rebuild
git init
git add .
git commit -m "init: rebuild sparkbot qwen assistant"
git branch -M main
git remote add origin https://github.com/<你的用户名>/sparkbot-qwen-assistant.git
git push -u origin main
```

## 重要提醒

- `.env` 不要提交；
- API Key 不要写入固件源码；
- 可以提交 `.env.example`；
- 如果使用原项目代码，注意 GPL 3.0 协议和原作者署名。
