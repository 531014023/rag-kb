# rag-kb

轻量级 RAG 知识库管理工具，支持混合搜索（dense vector + BM25 sparse）。

## 特性

- **混合搜索**：Dense vector 语义检索 + BM25 关键词匹配，RRF 融合
- **多种部署**：Docker 一键部署 or 本地 pip 安装
- **FastAPI 服务**：提供 REST API，方便集成
- **CLI 工具**：命令行操作知识库

## 快速开始

### Docker 部署（推荐）

```bash
# 构建并启动 Qdrant + API 服务
docker-compose up -d rag-api

# API 地址：http://localhost:12007
# Qdrant Dashboard：http://localhost:6333/dashboard
```

### 本地安装

```bash
# 安装
pip install -e .

# 确保 Qdrant 运行
docker run -d --name qdrant -p 6333:6333 qdrant/qdrant:v1.7.4

# 启动 API 服务
rag-server
```

## 配置

编辑 `config.yaml`：

```yaml
# 服务配置
server:
  host: "0.0.0.0"      # 监听地址
  port: 8081           # 监听端口
  upload_dir: "uploads" # 上传文件临时目录

# Qdrant 配置
qdrant:
  host: "localhost"    # Docker 部署时用 "qdrant"
  port: 6333
  grpc_port: 6334
  collection_default:
    vector_size: 1024   # 与 embedding 模型匹配
    distance: "COSINE"  # COSINE | EUCLID | DOT
  enable_sparse: true   # 是否启用 BM25 sparse vector（混合搜索）

# Embedding 配置（支持 local / custom）
embedding:
  type: custom
  api_url: "http://127.0.0.1:11234/v1/embeddings"
  model: "text-embedding-qwen3-embedding-0.6b"
  timeout: 30

# 分块配置
chunking:
  chunk_size: 800
  chunk_overlap: 100

# CLI 默认值
default_collection: default
default_top_k: 10
max_top_k: 20
```

## API 端点

### GET /health

健康检查。

**响应：**
```json
{"status": "ok"}
```

---

### GET /collections

列出所有 collections。

**响应：**
```json
{
  "success": true,
  "collections": ["default", "投资", "技术"]
}
```

---

### POST /upload

上传文件（multipart/form-data）。

**参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| file | File | 是 | 上传的文件 |
| collection | string | 否 | 目标 collection，默认 "default" |

**示例：**
```bash
curl -X POST http://localhost:8081/upload \
  -F "file=@./docs/article.pdf" \
  -F "collection=投资"
```

**响应：**
```json
{
  "success": true,
  "doc_id": "abc123",
  "chunks": 5
}
```

---

### POST /upload-text

上传文本内容。

**请求体：**
```json
{
  "text": "文档内容...",
  "collection": "default",
  "source": "api"
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| text | string | 是 | 文本内容 |
| collection | string | 否 | 目标 collection，默认 "default" |
| source | string | 否 | 来源标识，默认 "api" |

**响应：**
```json
{
  "success": true,
  "doc_id": "def456",
  "chunks": 3
}
```

---

### POST /search

检索。

**请求体：**
```json
{
  "query": "什么是安全边际",
  "collection": "default",
  "top_k": 5
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| query | string | 是 | 检索查询 |
| collection | string | 否 | 目标 collection，默认 "default" |
| top_k | integer | 否 | 返回数量，默认 5，最大 20 |

**响应：**
```json
{
  "success": true,
  "results": [
    {
      "content": "安全边际是指...",
      "metadata": {"doc_id": "abc123", "source": "article.pdf", "chunk_index": 0},
      "score": 0.85
    }
  ],
  "message": "检索到 5 条结果"
}
```

---

### POST /delete

删除文档。

**请求体：**
```json
{
  "doc_id": "abc123",
  "collection": "default"
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| doc_id | string | 是 | 文档 ID |
| collection | string | 否 | 目标 collection，默认 "default" |

**响应：**
```json
{
  "success": true,
  "message": "已删除 doc_id=abc123"
}
```

---

## CLI 命令

```bash
# 上传文件
rag upload ./docs/article.pdf -c 投资

# 上传文本
rag upload-text "巴菲特的投资理念" -c 投资

# 检索
rag search "什么是安全边际" -c 投资 -k 5

# 删除文档
rag delete abc123 -c 投资

# 列出所有 collections
rag list
```

## 支持的文件格式

使用 MarkItDown 解析，支持以下文件格式：

| 类型 | 扩展名 |
|------|--------|
| PDF | `.pdf` |
| PowerPoint | `.pptx`, `.ppt` |
| Word | `.docx`, `.doc` |
| Excel | `.xlsx`, `.xls` |
| EPUB | `.epub` |
| HTML | `.html`, `.htm` |
| 文本 | `.txt`, `.md` |
| 结构化文本 | `.csv`, `.json`, `.xml` |
| ZIP | `.zip`（遍历并转换其中每个文件） |

## 项目结构

```
rag-kb/
├── src/rag_kb/          # 核心库
│   ├── core.py          # 主逻辑
│   ├── vector_store.py  # Qdrant 操作
│   ├── embedding.py     # Embedding 接口
│   ├── document_parser.py
│   ├── text_chunker.py
│   └── config.py        # 配置加载
├── scripts/
│   └── server.py        # FastAPI 服务入口
├── config.yaml          # 配置文件
├── docker-compose.yml   # Docker 部署配置
├── Dockerfile           # 应用镜像
└── pyproject.toml       # 项目配置
```

## 架构

```
用户/Agent → HTTP API → rag-kb 服务 → Qdrant (向量数据库)
                    ↓
              Embedding 服务
                    ↓
              本地/远程 embedding 模型
```

## 开发

```bash
# 安装依赖
pip install -e ".[dev]"

# 代码格式
black src/

# lint
ruff check src/
```