## Demo-for-FakeLLM

演示专用：本项目是一个「类似豆包检索」的简化 Demo，支持：

- **管理员后台**：管理员登录后，可创建员工账号（用户名/初始密码/角色）。
- **员工问答界面**：员工使用账号登录后，可以输入文字问题，或上传现场照片发起提问。
- **后端 API**：FastAPI 实现登录、权限控制、提问记录等；预留了 RAG + 多模态大模型接入位置。
- **移动端友好前端**：基于 React + Vite，页面布局对手机浏览器比较友好。

> 说明：当前仓库中的「回答」逻辑只是一个占位 Demo，会把你的问题原样回显。真正的 RAG（向量检索）+ 中文大模型、以及根据货架图片给出摆放建议，可以按下面的方案逐步接入。

---

## 一、整体方案（可以给你哥们看的版本）

### 1. 总体架构

- **终端**：网页（手机浏览器为主，后续可封装成小程序 / WebView）。
- **前端**：`frontend`（React + Vite），包含：
  - 登录页：管理员 / 员工用同一登录入口。
  - 管理员后台：账号分配、查看账号列表。
  - 员工问答页：文字 + 图片提问，展示当前会话历史回答。
- **后端**：`backend`（FastAPI）：
  - 用户 & 权限：SQLite + SQLAlchemy + JWT 鉴权（区分 `admin` / `employee`）。
  - 提问记录：把每次提问和回答存到数据库。
  - RAG 占位：`app/rag.py` 里预留了函数，未来接入向量数据库 + 多模态模型。
- **大模型服务**（你可以单独部署，或直接买云上的）：
  - **文本检索 &问答**：推荐用 RAG：
    - 向量模型：`bge-m3` / `bge-large-zh` 等中文向量模型。
    - 向量库：`FAISS` / `Chroma` / `pgvector` 均可。
    - 大模型：`Qwen2.5-7B-Instruct`、`Yi-1.5-9B-Chat` 等中文效果比较好的开源模型，或直接调用豆包 / 通义 / 文心等云端模型 API。
  - **图片理解 & 布局建议**（高级需求）：
    - 第一阶段：只做「图像检索」——用 CLIP / EVA-CLIP 提取图片向量，找相似场景的标准示意图，然后用文本大模型生成描述性答案。
    - 第二阶段：引入目标检测 / grounding 模型（如 GroundingDINO + SAM / RT-DETR 等），在图片中画出推荐摆放区域，然后返回坐标或直接生成叠加框。

你现在仓库里的代码，已经把「账号体系 + 问答入口 + 后端占位」全部搭好，后续只需要在 `rag.py` 里真正接入你选好的模型和向量库即可。

---

## 二、本地运行步骤（演示用）

### 1. 启动后端（FastAPI）

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows 用 .venv\Scripts\activate
pip install -r requirements.txt

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

启动后：

- 健康检查接口：`GET http://localhost:8000/health`
- 默认管理员账号（首次启动自动创建）：
  - 用户名：`admin`
  - 密码：`admin123`

> 生产环境请修改 `app/security.py` 里的 `SECRET_KEY`，并在数据库里改掉默认管理员密码。

### 2. 启动前端（React）

```bash
cd frontend
npm install
npm run dev
```

默认会在 `http://localhost:5173` 打开前端页面。

前端默认把后端地址当成 `http://localhost:8000`，如果你要改成线上地址，可以在 `frontend` 根目录创建 `.env` 文件，例如：

```bash
VITE_API_BASE_URL=https://your-api-domain.com
```

---

## 三、使用流程说明

### 1. 管理员分配账号

1. 用浏览器打开前端地址（手机 / 电脑都可以）：`http://localhost:5173`
2. 使用默认管理员账号登录：
   - 用户名：`admin`
   - 密码：`admin123`
3. 进入「管理员后台」页面：
   - 输入员工用户名、初始密码。
   - 角色选择 `员工`（默认就是 employee）。
   - 点击「创建账号」，即可为一线工人创建登录账户。

### 2. 员工登录 & 提问

1. 员工拿到自己的账号密码后，在同一个登录页输入：
   - 用户名：管理员分配的用户名。
   - 密码：管理员设置的初始密码。
2. 登录成功后自动跳转到「员工问答」页面：
   - 输入文字问题，例如：*这批 80cm × 40cm 的箱子，货架 A3 这一层怎么摆放比较合理？*
   - 可以选择上传一张现场拍的照片（当前只是传到后端，占位不做真实识别）。
   - 点击「提交问题」，稍后会在下方看到 Demo 回答。

> 现在的回答是「占位文案」，等你接好 RAG + 大模型之后，就会变成真正的智能回答。

---

## 四、如何基于现有代码接入真正的 RAG + 模型

下面是一条你可以跟进实现的路线，重点是你只需要在 `rag.py` 里动手，其它前后端都不用大改。

### 1. 文本 RAG（知识库问答）

1. **确定知识来源**：
   - 仓库作业指导书（Word / PDF）
   - 安全手册
   - 商品/货架编码规则
2. **离线预处理**（可以单独写一个脚本，不一定放在本项目里）：
   - 把文档转成纯文本。
   - 切分成段落（按标题 / 段落 / 固定 token 数）。
   - 调用中文向量模型（如 `bge-m3`）生成向量。
   - 向量 + 原文一起写入向量数据库（FAISS / Chroma / pgvector）。
3. **在线检索流程（写到 `rag.py`）**：
   - `get_rag_answer(text, image_bytes=None)`：
     - 对 `text` 编码成向量。
     - 在向量库中检索 Top-K 相似段落。
     - 把检索到的内容和用户问题一起丢给大模型，让模型「根据公司内部标准回答」。
   - 返回结构里把 `answer` 和 `sources`（命中的文档片段）一并返回，方便以后前端展示引用来源。

### 2. 图片理解（从照片里看摆放是否合理）

短期可以做一个**折中方案**，不用上来就做画框：

- 把现场照片用 CLIP 之类的视觉模型编码成向量；
- 用同一模型把「标准摆放示意图」库里的图片也编码好；
- 做图像向量检索，找到最像的标准图片；
- 再把「标准图片 + 说明文字 + 员工现场图」喂给大模型，让它用中文解释「哪里不对、应该怎么改」。

真正要实现「在图片上画一个推荐摆放区域」，可以在第二阶段：

- 使用 **GroundingDINO / RT-DETR** 做检测，把货架的层、货物类型检测出来；
- 再结合规则或大模型，算出应该放到哪一层 / 哪个区域；
- 返回一个带有坐标的结果（比如 JSON 里有 `x, y, w, h`），前端可以在图片上画出一个框。

这些算法可以优先在单独的 notebook / 脚本里调通，再接到 `rag.py` 对应逻辑里。

---

## 五、代码结构一览

- `backend/`
  - `requirements.txt`：后端依赖。
  - `app/main.py`：FastAPI 入口，挂载路由、CORS、启动时初始化数据库和默认管理员。
  - `app/database.py`：SQLite 数据库连接配置。
  - `app/models.py`：`User` / `Question` 等 ORM 模型。
  - `app/schemas.py`：Pydantic 模型（请求/响应）。
  - `app/security.py`：密码哈希 + JWT 生成/解析（记得改 `SECRET_KEY`）。
  - `app/deps.py`：依赖注入（获取当前用户/管理员/员工）。
  - `app/routers_auth.py`：登录接口 `/auth/login`，以及默认管理员创建逻辑。
  - `app/routers_admin.py`：管理员相关接口（列表用户、创建用户）。
  - `app/routers_chat.py`：员工提问接口 `/chat/query`。
  - `app/rag.py`：**RAG + 大模型接入的占位文件**（你主要改这里）。
- `frontend/`
  - `index.html`：前端入口 HTML。
  - `vite.config.ts` / `tsconfig.json` / `package.json`：前端工程配置。
  - `src/styles.css`：简单的移动端友好样式。
  - `src/main.tsx`：React 入口。
  - `src/App.tsx`：路由定义（登录 / 管理员 / 员工问答）。
  - `src/api.ts`：封装调用后端 API 的方法。
  - `src/pages/Login.tsx`：登录页。
  - `src/pages/AdminDashboard.tsx`：管理员后台（分配账号）。
  - `src/pages/EmployeeChat.tsx`：员工问答页（文字 + 图片上传）。

---

## 六、数据库与并发能力说明（FastAPI + PostgreSQL）

- **FastAPI 本身**：基于 asyncio，配合 Uvicorn / Gunicorn，可以轻松支撑几百并发连接，对「几百人日常使用」完全足够。
- **当前 Demo**：默认使用本地 SQLite，仅用于演示和小规模测试。
- **生产环境推荐**：切换到 PostgreSQL：
  - 已在 `app/database.py` 中支持通过环境变量 `DATABASE_URL` 指定数据库：
    - 默认：`sqlite:///./app.db`
    - PostgreSQL 示例：`postgresql+psycopg2://user:password@host:5432/dbname`
  - 启动前，在后端目录设置环境变量即可，例如：

```bash
export DATABASE_URL="postgresql+psycopg2://user:password@127.0.0.1:5432/fakellm"
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

> 实际部署时，可以用多进程（Gunicorn+Uvicorn workers）、连接池（SQLAlchemy 默认支持）来进一步提高并发能力。

---

## 七、安全与访问方案：局域网 + VPN / HTTPS

### 1. 基础假设

- 系统部署在公司一台电脑/服务器上（运行本项目后端 + 前端）。
- 员工使用**手机或电脑**访问这个服务。
- 需求：不要把服务曝露到公网，尽可能做到「只有内部人能访问」且**传输加密**。

### 2. 推荐方案 A：Tailscale / ZeroTier 等 VPN 组网

1. 在服务器和每个需要访问的客户端（手机 / 电脑）上安装 Tailscale（或 ZeroTier）。
2. 登录同一个账号/网络后，会自动形成一个虚拟专网，每台设备都有一个虚拟 IP。
3. 服务器上跑本项目（例如 `http://0.0.0.0:8000` 后端，`http://0.0.0.0:5173` 前端），
   - 手机上用浏览器访问服务器的 **虚拟 IP + 端口**，例如：`http://100.x.x.x:5173`。
4. VPN 本身使用 WireGuard 等协议加密传输，相当于在公网之上又包了一层加密隧道。

特点：

- 无需公网 IP、无需配置复杂的 HTTPS 证书。
- 所有流量在 VPN 隧道内传输，外界无法窃听。

### 3. 推荐方案 B：局域网 + 自签 HTTPS 反向代理

如果你希望直接用 `https://` 访问，可以在服务器上增加一层反向代理：

1. 使用 Nginx 或 Caddy 作为反向代理：
   - 反向到后端：`http://127.0.0.1:8000`
   - 提供静态前端：构建 `frontend` 后的静态文件。
2. 使用自签证书或者通过 `mkcert` 在局域网环境生成受信任证书：
   - 在服务器上安装证书；
   - 在公司手机/电脑上导入 CA 证书（一次性操作）。
3. 员工通过 `https://your-lan-hostname` 访问，浏览器与反向代理之间是 TLS 加密。

### 4. 静态数据加密与敏感信息保护

- **磁盘加密**：推荐在操作系统层面开启磁盘加密（macOS FileVault、Windows BitLocker）。
- **配置与密钥**：
  - 不要把 `SECRET_KEY`、数据库密码、云厂商 API Key 等提交到 git。
  - 使用环境变量或单独的配置文件（.env，本地保存、不进仓库）。
- **字段级加密（可选）**：
  - 对特别敏感的数据（比如员工手机号、业务密钥），可以在写入数据库前用对称加密（AES 等）加密，读取时再在应用层解密。

> 严格意义上的「端到端加密」是服务器也看不到明文（例如 Signal），与你这个需要在服务器做 RAG 和模型推理的场景冲突。这里给出的方案是：**客户端 ↔ 你的服务器 传输加密 + 服务器本机数据加密**，在工程上已经是比较稳妥的做法。

