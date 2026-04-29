"""
文档解析模块 - 使用 Unstructured 解析多种文档格式
支持: PDF, PowerPoint, Word, Excel, HTML, EPUB, Markdown, TXT, CSV, JSON, XML, ZIP
"""
from pathlib import Path
from typing import Any

from unstructured.partition.auto import partition
from unstructured.chunking.title import chunk_by_title


def _serialize_metadata(meta: Any) -> dict:
    """序列化 metadata，避免 Path 对象等不可序列化问题"""
    if meta is None:
        return {}
    result = {}
    for k, v in meta.items() if hasattr(meta, "items") else {}:
        if isinstance(v, Path):
            result[k] = str(v)
        elif isinstance(v, (list, tuple)):
            result[k] = [_serialize_metadata(item) if isinstance(item, dict) else str(item) if isinstance(item, Path) else item for item in v]
        elif isinstance(v, dict):
            result[k] = _serialize_metadata(v)
        else:
            try:
                result[k] = v
            except Exception:
                result[k] = str(v)
    return result


class DocumentParser:
    """使用 Unstructured 解析文档，保持结构化元素"""

    def __init__(self):
        pass

    def parse(self, file_path: str) -> list[dict]:
        """解析文档返回结构化元素列表"""
        elements = partition(filename=str(file_path))
        return [
            {
                "type": elem.category,
                "text": str(elem),
                "metadata": _serialize_metadata(getattr(elem.metadata, "to_dict", lambda: {})()),
            }
            for elem in elements
        ]

    def parse_and_chunk(self, file_path: str, chunk_size: int = 500) -> list[dict]:
        """解析文档并分块，返回文本块列表"""
        elements = partition(filename=str(file_path))

        # 使用 chunk_by_title 按标题切分，表格保持完整
        chunks = chunk_by_title(
            elements,
            max_characters=chunk_size,
            skip_table_chunking=True,
        )

        return [
            {
                "text": str(chunk),
                "type": chunk.category,
            }
            for chunk in chunks
        ]

    def parse_text(self, text: str) -> list[dict]:
        """文本直接返回为单个元素"""
        return [{"type": "NarrativeText", "text": text.strip(), "metadata": {}}]