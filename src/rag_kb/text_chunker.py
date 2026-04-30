"""
分块模块 - 基于 SemanticChunker 的语义分块
"""
from __future__ import annotations

from typing import Optional

from chonkie import SemanticChunker


class TextChunker:
    """语义分块器，使用 chonkie SemanticChunker 按句子相似度切分"""

    def __init__(
        self,
        chunk_size: int = 500,
        threshold: float = 0.8,
        similarity_window: int = 3,
        min_sentences_per_chunk: int = 1,
        min_characters_per_sentence: int = 10,
        delim: Optional[list[str]] = None,
        embedding_model: str = "minishlab/potion-base-32M",
    ):
        self.chunk_size = chunk_size
        self.threshold = threshold
        self.similarity_window = similarity_window
        self.min_sentences_per_chunk = min_sentences_per_chunk
        self.min_characters_per_sentence = min_characters_per_sentence
        self.delim = delim or ["。", "！", "？", "……", "\n"]
        self.embedding_model = embedding_model
        self._chunker: Optional[SemanticChunker] = None

    def _get_chunker(self) -> SemanticChunker:
        if self._chunker is None:
            self._chunker = SemanticChunker(
                chunk_size=self.chunk_size,
                threshold=self.threshold,
                similarity_window=self.similarity_window,
                min_sentences_per_chunk=self.min_sentences_per_chunk,
                min_characters_per_sentence=self.min_characters_per_sentence,
                delim=self.delim,
                embedding_model=self.embedding_model,
            )
        return self._chunker

    def chunk(self, text: str) -> list[dict]:
        """将纯文本切分为语义块"""
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
