"""
分块模块 - 使用 Chonkie RecursiveChunker
"""
from chonkie import RecursiveChunker


class TextChunker:
    """使用 Chonkie RecursiveChunker 进行文本分块

    按层级递归切分：段落 -> 句子 -> 词，保留语义完整性
    """

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        # RecursiveChunker 不支持 overlap，用 chunk_size 控制
        self.chunker = RecursiveChunker(
            tokenizer='character',
            chunk_size=chunk_size
        )

    def chunk(self, text: str) -> list[str]:
        """返回文本块列表"""
        if not text or not text.strip():
            return []
        chunks = self.chunker(text)
        return [c.text for c in chunks]

    def chunk_texts(self, texts: list[str]) -> list[str]:
        """分块多个文本段落"""
        result = []
        for text in texts:
            result.extend(self.chunk(text))
        return result