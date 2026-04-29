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
# 启动 Qdrant + API 服务
docker-compose up -d api

# API 地址：http://localhost:8081
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
# Qdrant 配置
qdrant:
  host: "localhost"      # Docker 部署时用 "qdrant"
  port: 6333
  grpc_port: 6334
  collection_default:
    vector_size: 1024    # 与 embedding 模型匹配
    distance: "COSINE"

# Embedding 配置（支持 local / custom）
embedding:
  type: custom
  api_url: "http://127.0.0.1:11234/v1/embeddings"
  model: "text-embedding-qwen3-embedding-0.6b"
```

## 使用方式

### API 服务

```bash
# 上传文件
curl -X POST http://localhost:8081/upload \
  -H "Content-Type: application/json" \
  -d '{"file_path": "./docs/article.md", "collection": "投资"}'

# 检索
curl -X POST http://localhost:8081/search \
  -H "Content-Type: application/json" \
  -d '{"query": "安全边际", "collection": "投资", "top_k": 5}'

# 列出 collections
curl http://localhost:8081/collections
```

### CLI

```bash
# 上传文件
rag upload ./docs/article.md -c 投资

# 上传文本
rag upload-text "巴菲特的投资理念" -c 投资

# 检索
rag search "什么是安全边际" -c 投资 -k 5

# 删除文档
rag delete doc_id_abc123 -c 投资

# 列出所有 collections
rag list
```

## 项目结构

```
rag-kb/
├── src/rag_kb/          # 核心库
│   ├── core.py          # 主逻辑
│   ├── vector_store.py  # Qdrant 操作
│   ├── embedding.py     # Embedding 接口
│   ├── document_parser.py
│   ├── text_chunker.py
│   └── server.py        # FastAPI 服务
├── scripts/
│   └── server.py        # 服务入口（可通过 rag-server 启动）
├── config.yaml          # 配置文件
├── docker-compose.yml   # Docker 部署配置
├── Dockerfile           # 应用镜像
└── pyproject.toml       # 项目配置
```

## API 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /health | 健康检查 |
| GET | /collections | 列出所有 collections |
| POST | /upload | 上传文件 |
| POST | /upload-text | 上传文本 |
| POST | /search | 检索 |
| POST | /delete | 删除文档 |

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