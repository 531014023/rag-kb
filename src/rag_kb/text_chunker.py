"""
分块模块 - 使用 RecursiveChunker 填充式分块，大小均衡，支持中文标点
"""
from __future__ import annotations

from typing import Optional

from chonkie import RecursiveChunker
from chonkie.types.recursive import RecursiveRules


# 不同文件类型的推荐分块策略
FILE_CHUNKER_STRATEGIES: dict[str, str] = {
    "text/markdown": "recursive",
    "text/x-markdown": "recursive",
    "text/html": "recursive",
    "application/pdf": "recursive",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "recursive",
    "application/epub+zip": "recursive",
    "application/epub": "recursive",
}


class TextChunker:
    """文本分块器"""

    def __init__(
        self,
        chunk_size: int = 800,
    ):
        self.chunk_size = chunk_size
        self._chunker: Optional[RecursiveChunker] = None

    def _get_chunker(self) -> RecursiveChunker:
        if self._chunker is None:
            rules = RecursiveRules.from_recipe(lang="zh")
            self._chunker = RecursiveChunker(chunk_size=self.chunk_size, rules=rules)
        return self._chunker

    def chunk(self, text: str) -> list[dict]:
        """将纯文本切分为块"""
        if not text or not text.strip():
            return []
        chunker = self._get_chunker()
        chunks = chunker.chunk(text)
        return [{"text": c.text, "type": "Text"} for c in chunks if c.text.strip()]

    def chunk_texts(self, texts: list[str]) -> list[dict]:
        """分块多个文本段落，先拼接再切分"""
        if not texts:
            return []
        combined = "\n\n".join(t for t in texts if t.strip())
        return self.chunk(combined)