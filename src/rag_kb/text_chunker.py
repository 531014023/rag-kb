"""
分块模块 - 使用 Unstructured 的 chunk_by_title
"""


class TextChunker:
    """保留接口兼容，分块逻辑已移至 DocumentParser"""

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk(self, text: str) -> list[str]:
        """纯文本分块，按字符硬切"""
        if not text or not text.strip():
            return []
        chunks = []
        for i in range(0, len(text), self.chunk_size):
            chunks.append(text[i : i + self.chunk_size])
        return chunks

    def chunk_texts(self, texts: list[str]) -> list[str]:
        """分块多个文本段落"""
        return [t for t in texts if t.strip()]