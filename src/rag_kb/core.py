"""
核心操作模块
"""
import hashlib
from pathlib import Path

from .config import config
from .document_parser import DocumentParser
from .text_chunker import TextChunker
from .vector_store import upload_chunks, search_chunks, delete_chunks, list_collections


def upload(file_path: str, collection_name: str = "default") -> dict:
    """上传文档"""
    try:
        # 解析文档
        parser = DocumentParser()
        text = parser.parse(file_path)

        # 分块
        chunk_cfg = config.get("chunking", {})
        chunker = TextChunker(
            chunk_size=chunk_cfg.get("chunk_size", 500),
            chunk_overlap=chunk_cfg.get("chunk_overlap", 50)
        )
        chunks = chunker.chunk(text)

        # 构建 chunk 数据
        doc_id = hashlib.md5(Path(file_path).name.encode()).hexdigest()
        chunk_data = [
            {"text": c, "doc_id": doc_id, "source": Path(file_path).name, "chunk_index": i}
            for i, c in enumerate(chunks)
        ]

        # 上传
        result = upload_chunks(collection_name, config, chunk_data)
        return {"success": True, "doc_id": doc_id, "chunks": len(chunk_data)}

    except Exception as e:
        return {"success": False, "message": str(e)}


def upload_text(text: str, collection_name: str = "default", source: str = "direct") -> dict:
    """上传文本"""
    try:
        doc_id = hashlib.md5(text.encode()).hexdigest()

        chunk_cfg = config.get("chunking", {})
        chunker = TextChunker(
            chunk_size=chunk_cfg.get("chunk_size", 500),
            chunk_overlap=chunk_cfg.get("chunk_overlap", 50)
        )
        chunks = chunker.chunk(text)

        chunk_data = [
            {"text": c, "doc_id": doc_id, "source": source, "chunk_index": i}
            for i, c in enumerate(chunks)
        ]

        result = upload_chunks(collection_name, config, chunk_data)
        return {"success": True, "doc_id": doc_id, "chunks": len(chunk_data)}
    except Exception as e:
        return {"success": False, "message": str(e)}


def search(query: str, collection_name: str = "default", top_k: int = 5) -> dict:
    """检索"""
    try:
        return search_chunks(query, collection_name, config, top_k)
    except Exception as e:
        return {"success": False, "results": [], "message": str(e)}


def delete(doc_id: str, collection_name: str = "default") -> dict:
    """删除文档"""
    try:
        return delete_chunks(doc_id, collection_name, config)
    except Exception as e:
        return {"success": False, "message": str(e)}


def list_all_collections() -> dict:
    """列出 collections"""
    return list_collections(config)