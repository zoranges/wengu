下面是一个**可直接放到你仓库里的 `README.md`**，内容是**工程级、可部署、可维护**的版本，完全贴合你当前的 FastAPI + OCR + LLM + Docker 项目现状，没有任何“幻觉式描述”。

你可以 **原样复制保存为 `README.md`**。

---

# 雯谷（Wengu）· 智能错题整理系统

雯谷（Wengu）是一个基于 **FastAPI + OCR + 大模型（LLM）** 的智能错题整理系统，支持 **图片上传 → 数学题识别 → 自动解析 → 错题存储与回溯**，可通过 **Docker 一键部署并对公网提供服务**。

---

## ✨ 功能特性

* 📷 **图片上传识别**

  * 支持 `.jpg / .jpeg / .png`
  * 使用 SimpleTex API 进行公式 / 数学文本 OCR

* 🧠 **AI 题目还原与解析**

  * 基于大模型（DashScope / Qwen）
  * 自动输出：

    * 规范题目
    * 知识点
    * 解题过程
    * 最终答案

* 🗂 **错题自动存储**

  * 使用 SQLite 本地数据库
  * 支持历史记录查询

* 🌐 **Web 访问**

  * 首页：产品入口（`index.html`）
  * 功能页：入谷（`入谷.html`）
  * 后端 API：FastAPI

* 🐳 **Docker 化部署**

  * 一条命令即可上线
  * 支持端口映射、公网访问

---

## 📁 项目结构

```text
/opt/wengu
├── main.py                 # FastAPI 主入口
├── ocr.py                  # SimpleTex OCR 调用
├── llm.py                  # 大模型题目解析
├── requirements.txt        # Python 依赖
├── Dockerfile              # Docker 构建文件
├── index.html              # 首页（产品入口）
├── 入谷.html               # 功能页面（上传题目）
├── mistakes_vangu.db       # SQLite 数据库（运行后生成）
├── uploads/                # 临时图片上传目录
└── __pycache__/
```

---

## 🚀 快速启动（Docker 推荐）

### 1️⃣ 构建镜像

```bash
docker build -t wengu-app .
```

---

### 2️⃣ 运行容器（公网访问）

```bash
docker run -d \
  --name wengu \
  -p 80:8000 \
  wengu-app
```

> 浏览器访问：
>
> * 首页：[http://服务器IP/](http://服务器IP/)
> * API 文档：[http://服务器IP/docs](http://服务器IP/docs)

---

## 🔌 API 接口说明

### `GET /`

* 功能：返回首页 `index.html`
* 用途：项目入口

---

### `POST /upload`

* 功能：上传题目图片并解析
* 请求类型：`multipart/form-data`
* 参数：

| 参数名  | 类型   | 说明   |
| ---- | ---- | ---- |
| file | File | 图片文件 |

* 返回示例：

```json
{
  "raw_ocr": "...",
  "ai_analysis": {
    "status": "success",
    "formatted_question": "...",
    "knowledge_points": "...",
    "analysis": "...",
    "answer": "..."
  }
}
```

---

### `GET /history`

* 功能：获取最近 20 条错题记录
* 返回：JSON 数组

---

## 🧠 OCR 与 LLM 说明

### OCR（ocr.py）

* 使用 **SimpleTex 标准公式识别接口**
* 采用 APP_ID + APP_SECRET 鉴权
* 支持 LaTeX 数学公式识别

---

### LLM（llm.py）

* 使用 DashScope / Qwen 模型
* 强制 JSON 输出
* 自动容错，避免解析失败导致系统崩溃

---

## 🗄 数据库说明

* 类型：SQLite
* 文件：`mistakes_vangu.db`
* 表结构：

```sql
mistakes (
  id INTEGER PRIMARY KEY,
  raw_text TEXT,
  status TEXT,
  formatted_question TEXT,
  knowledge_points TEXT,
  analysis TEXT,
  answer TEXT,
  created_at DATETIME
)
```

---




---

## 📌 未来规划（可选）

* 用户系统（账号 / 学生）
* 错题分类与标签
* 多学科支持

---

## 📜 License

仅供学习与研究使用。

