# 智能制造 RAG 知识库问答系统 (Demo)

本项目是一个专为制造业场景（如工厂车间、仓储物流）设计的「类似豆包的智能问答」系统。
包含前后端完整链路，核心能力是 **RAG（检索增强生成）** 和 **多模态大模型（看图说话）**。

## 🌟 核心功能

1. **管理员后台**：创建员工账号，上传企业内部知识库文档（.txt）。
2. **纯本地向量检索**：上传的文档会自动分块并在本地 **ChromaDB** 中向量化（使用 Ollama 跑 `nomic-embed-text` 模型）。
3. **员工多模态问答**：员工登录后可发送文字问题或上传现场照片，系统会自动从知识库检索相关规定，并结合大模型给出专业回答。
4. **数据绝对安全**：完全本地化运行（SQLite + ChromaDB + Ollama），无需懂公网穿透，完美适配国企保密要求。

---

## 💻 Windows 本地一键部署指南

以下步骤专为 **Windows 笔记本/台式机** 编写。只要你的电脑装了 Docker，即可一键启动所有相关服务。

### 1. 前置准备

- 安装 **Docker Desktop for Windows**（安装时请勾选使用 WSL 2 后端）。
- 如果你的 Windows 电脑有 **NVIDIA 显卡**（推荐），Docker Desktop 会自动利用它加速 Ollama 模型推理。

### 2. 获取代码与启动

打开 PowerShell 或 CMD，进入项目根目录：

```cmd
# 启动所有容器（前端、后端、向量数据库、Ollama大模型服务）
# 第一次运行大约需要几分钟下载镜像
docker compose up -d --build
```

启动成功后，可以查看容器运行状态：
```cmd
docker ps
```
你应该能看到 4 个容器状态均为 `Up`：`frontend`, `backend`, `chromadb`, `ollama`。

### 3. 下载大模型（关键一步）

系统虽然启动了，但此时 Ollama 肚子里还是空的。你需要手动让它下载我们需要的两个模型。

在 Windows 终端（PowerShell / CMD）中依次执行以下两条命令（建议开启全局代理以加快下载速度）：

**下载嵌入模型（用于知识库 RAG 检索，约 274MB）：**
```cmd
docker exec -it ollama ollama pull nomic-embed-text
```

**下载多模态对话大模型（推荐阿里 Qwen2.5-VL，强推中文+看图能力，约 6GB）：**
```cmd
docker exec -it ollama ollama pull qwen2.5vl:7b
```
*(注：如果你的电脑内存/显存比较小，最后一条命令可以换成较小的模型 `docker exec -it ollama ollama pull qwen2.5vl:3b`)*

### 4. 开始使用

一切就绪！打开浏览器访问：

👉 **http://localhost:5173**

**第一步：管理员上传知识卡片**
1. 用默认管理员账号登录：
   - 账号：`admin`
   - 密码：`admin123`
2. 进入「RAG 知识库管理」，上传你需要测试的 `.txt` 文件（仓库代码的 `sample_data/` 目录下有几份写好的工厂文档样例）。
3. 上传后，后台会自动把文件切块并存入 ChromaDB，此过程需等待几秒钟。

**第二步：员工提问测试**
1. 在管理员后台创建一个员工测试账号。
2. 退出管理员，用员工账号重新登录。
3. 试着问一个刚才上传的文档里的问题（比如：“重型设备该放哪层？”），或传一张照片测试它的理解能力！

---

## 🛠️ 后续二次开发与调试

本系统的后端基于 **FastAPI (Python)**，前端基于 **React + Vite**。

如果想修改代码（比如在 `backend/app/rag.py` 中调整系统提示词）：
1. 修改本地代码保存。
2. 运行 `docker compose up -d --build backend` 重新构建并重启后端。
3. 你的数据（SQLite 存的账号记录、ChromaDB 存的向量数据、Ollama 下载的模型）**全部持久化在 Docker Volume 中，重启/重建容器绝对不会丢失。**
