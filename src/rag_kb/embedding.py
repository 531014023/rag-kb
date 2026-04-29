"""
Embedding 模块 - HTTP API embedding（LM Studio 等兼容）
"""
import requests
from typing import List, Optional


class HTTPEmbedding:
    """HTTP API embedding（LM Studio 等兼容）"""

    def __init__(self, api_url: str, api_key: Optional[str] = None,
                 model: Optional[str] = None, timeout: float = 60.0):
        self.api_url = api_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.timeout = timeout

    def embed(self, text: str) -> List[float]:
        """获取文本的 embedding 向量"""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        payload = {"input": text}
        if self.model:
            payload["model"] = self.model
        resp = requests.post(self.api_url, headers=headers, json=payload, timeout=self.timeout)
        resp.raise_for_status()
        result = resp.json()
        if "data" in result:
            return result["data"][0]["embedding"]
        elif "embedding" in result:
            return result["embedding"]
        return result[0] if isinstance(result, list) else result

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """批量获取 embedding"""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        payload = {"input": texts}
        if self.model:
            payload["model"] = self.model
        resp = requests.post(self.api_url, headers=headers, json=payload, timeout=self.timeout)
        resp.raise_for_status()
        result = resp.json()
        if "data" in result:
            return [item["embedding"] for item in result["data"]]
        return result


class LocalEmbedding:
    """本地 sentence-transformers 模型"""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer(model_name)

    def embed(self, text: str) -> List[float]:
        return self.model.encode([text]).tolist()[0]

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        return self.model.encode(texts).tolist()


def create_embedding_from_config(cfg: dict):
    """根据配置创建 Embedding"""
    emb_type = cfg.get("type", "custom")
    if emb_type == "local":
        return LocalEmbedding(cfg.get("model", "all-MiniLM-L6-v2"))
    return HTTPEmbedding(
        api_url=cfg.get("api_url", "http://127.0.0.1:8080/embed"),
        api_key=cfg.get("api_key"),
        model=cfg.get("model"),
        timeout=cfg.get("timeout", 60.0)
    )