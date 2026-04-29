"""
RAG Knowledge Base - 轻量级向量知识库
"""
from .core import upload, upload_text, search, delete, list_all_collections
from .config import config

__all__ = ["upload", "upload_text", "search", "delete", "list_all_collections", "config"]
__version__ = "1.0.0"