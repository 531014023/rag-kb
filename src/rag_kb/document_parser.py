"""
文档解析模块 - 使用 MarkItDown 解析多种文档格式
支持: PDF, PowerPoint, Word, Excel, HTML, EPUB, Markdown, TXT, CSV, JSON, XML, ZIP
"""
from markitdown import MarkItDown


class DocumentParser:
    """使用 MarkItDown 解析文档为 Markdown 文本"""

    def __init__(self):
        self._converter = MarkItDown()

    def parse(self, file_path: str) -> str:
        """解析文档返回 Markdown 文本"""
        result = self._converter.convert(file_path)
        return result.text_content

    def parse_text(self, text: str) -> str:
        """文本直接返回"""
        return text.strip()