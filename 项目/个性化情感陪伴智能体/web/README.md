# Web 控制台（二期）

Vite + React + TypeScript + Tailwind。与 FastAPI 后端联调。

## 快速开始

1. **先**在项目根目录启动后端（默认 `http://127.0.0.1:8076`），见根目录 **`README.md`**。
2. 在本目录执行：

```bash
npm install
npm run dev
```

3. 开发时浏览器访问 `http://127.0.0.1:5173`（以终端为准）。API 请求使用 **`/api`**，由 Vite 代理到后端。

## 环境变量

复制 **`.env.example`** 为 `.env`（可选）：

| 变量 | 说明 |
|------|------|
| `VITE_DEV_API_TARGET` | 开发代理目标，默认 `http://127.0.0.1:8076` |
| `VITE_API_BASE` | **仅生产构建**：后端根 URL，无尾斜杠 |

## 构建

```bash
npm run build
```

构建前若部署到与 API 不同源，请设置 `VITE_API_BASE`。

---

完整说明（虚拟环境、pytest、Gradio 等）见 **项目根目录 `README.md`** 与 **`#Personal_Documents/常用命令.md`**。
