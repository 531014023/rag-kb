"""
向量存储模块 - 使用 qdrant-client 直连，支持混合搜索
"""
import hashlib
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.models import PointStruct, Filter, FieldCondition, MatchValue, SparseVector, FusionQuery, Fusion
from rank_bm25 import BM25Okapi


def get_client(config: dict) -> QdrantClient:
    """获取 Qdrant 客户端"""
    qdrant_cfg = config.get("qdrant", {})
    host = qdrant_cfg.get("host", "localhost")
    port = qdrant_cfg.get("port", 6333)
    grpc_port = qdrant_cfg.get("grpc_port", 6334)
    return QdrantClient(host=host, port=port, grpc_port=grpc_port, check_compatibility=False)


def ensure_collection(client: QdrantClient, collection_name: str, config: dict):
    """确保 collection 存在，不存在则创建"""
    qdrant_cfg = config.get("qdrant", {})
    vector_size = qdrant_cfg.get("collection_default", {}).get("vector_size", 1024)
    distance_str = qdrant_cfg.get("collection_default", {}).get("distance", "COSINE")
    enable_sparse = qdrant_cfg.get("enable_sparse", True)

    dist_map = {"COSINE": models.Distance.COSINE, "EUCLID": models.Distance.EUCLID, "DOT": models.Distance.DOT}
    dense_cfg = models.VectorParams(size=vector_size, distance=dist_map.get(distance_str, models.Distance.COSINE))
    sparse_cfg = {"sparse": models.SparseVectorParams()} if enable_sparse else None

    try:
        client.get_collection(collection_name)
    except:
        client.create_collection(
            collection_name=collection_name,
            vectors_config={"dense": dense_cfg},
            sparse_vectors_config=sparse_cfg
        )


def _tokenize(text: str) -> list[str]:
    """简单分词"""
    return text.lower().split()


def _compute_bm25_sparse(texts: list[str]) -> list[dict]:
    """计算 BM25 sparse 向量"""
    tokenized = [_tokenize(t) for t in texts]
    bm25 = BM25Okapi(tokenized)

    sparse_vectors = []
    for tokens in tokenized:
        scores = bm25.get_scores(tokens)
        # 取最高的几个词作为 sparse vector
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:20]
        indices = []
        values = []
        for idx in top_indices:
            if scores[idx] > 0:
                indices.append(idx)
                values.append(scores[idx])
        if indices:
            sparse_vectors.append({"indices": indices, "values": values})
        else:
            sparse_vectors.append({"indices": [0], "values": [0.0]})
    return sparse_vectors


def _build_points(chunks: list[dict], vectors: list, sparse_vectors: list | None, config: dict) -> list[PointStruct]:
    """构建 Qdrant points"""
    from .embedding import create_embedding_from_config
    points = []
    for i, (chunk, vector) in enumerate(zip(chunks, vectors)):
        unique_id = int(hashlib.md5(f"{chunk['doc_id']}_{chunk['chunk_index']}".encode()).hexdigest()[:8], 16)
        point_dict = {"dense": vector}
        qdrant_cfg = config.get("qdrant", {})
        if qdrant_cfg.get("enable_sparse", True) and sparse_vectors:
            point_dict["sparse"] = sparse_vectors[i]
        points.append(PointStruct(
            id=unique_id,
            vector=point_dict,
            payload={
                "text": chunk["text"],
                "doc_id": chunk["doc_id"],
                "source": chunk["source"],
                "chunk_index": chunk["chunk_index"]
            }
        ))
    return points


def upload_chunks(collection_name: str, config: dict, chunks: list[dict]) -> dict:
    """
    上传文本块到 Qdrant（dense + sparse 混合存储），批量上传避免超限

    chunks: [{"text": str, "doc_id": str, "source": str, "chunk_index": int}, ...]
    """
    from .embedding import create_embedding_from_config
    emb_cfg = config.get("embedding", {})
    embed_model = create_embedding_from_config(emb_cfg)

    client = get_client(config)
    ensure_collection(client, collection_name, config)

    # 计算所有 dense 和 sparse 向量
    texts = [c["text"] for c in chunks]
    vectors = embed_model.embed_batch(texts)

    qdrant_cfg = config.get("qdrant", {})
    enable_sparse = qdrant_cfg.get("enable_sparse", True)
    sparse_vectors = _compute_bm25_sparse(texts) if enable_sparse else None

    # 批量构建 points，每批最多 256 个（Qdrant 限制），逐批上传避免超时
    batch_size = 256
    total = len(chunks)
    for start in range(0, total, batch_size):
        end = min(start + batch_size, total)
        batch_chunks = chunks[start:end]
        batch_vectors = vectors[start:end]
        batch_sparse = sparse_vectors[start:end] if sparse_vectors else None
        points = _build_points(batch_chunks, batch_vectors, batch_sparse, config)
        client.upsert(collection_name=collection_name, points=points, wait=True)

    return {"success": True, "count": total}


def search_chunks(query: str, collection_name: str, config: dict, top_k: int = 5) -> dict:
    """
    混合搜索 Qdrant（dense + sparse RRF 融合）

    返回: {"success": True, "results": [{"text": str, "metadata": dict, "score": float}, ...]}
    """
    from .embedding import create_embedding_from_config
    emb_cfg = config.get("embedding", {})
    embed_model = create_embedding_from_config(emb_cfg)

    client = get_client(config)
    qdrant_cfg = config.get("qdrant", {})
    enable_sparse = qdrant_cfg.get("enable_sparse", True)

    # Dense query vector
    query_vector = embed_model.embed(query)

    # Sparse query vector (BM25)
    if enable_sparse:
        sparse_vectors = _compute_bm25_sparse([query])
        sparse_query = SparseVector(
            indices=sparse_vectors[0]["indices"],
            values=sparse_vectors[0]["values"]
        )
    else:
        sparse_query = None

    # 混合搜索
    if enable_sparse and sparse_query:
        results = client.query_points(
            collection_name=collection_name,
            prefetch=[
                {"query": query_vector, "using": "dense", "limit": top_k * 2},
                {"query": sparse_query, "using": "sparse", "limit": top_k * 2},
            ],
            query=FusionQuery(fusion=Fusion.RRF),
            limit=top_k,
            with_payload=True
        )
    else:
        results = client.query_points(
            collection_name=collection_name,
            query=query_vector,
            using="dense",
            limit=top_k,
            with_payload=True
        )

    return {
        "success": True,
        "results": [
            {
                "content": r.payload.get("text", ""),
                "metadata": {k: v for k, v in r.payload.items() if k != "text"},
                "score": r.score
            }
            for r in results.points
        ],
        "message": f"检索到 {len(results.points)} 条结果"
    }


def delete_chunks(doc_id: str, collection_name: str, config: dict) -> dict:
    """删除指定 doc_id 的所有 chunks"""
    client = get_client(config)

    client.delete(
        collection_name=collection_name,
        points_selector=Filter(
            must=[
                FieldCondition(key="doc_id", match=MatchValue(value=doc_id))
            ]
        ),
        wait=True
    )
    return {"success": True, "message": f"已删除 doc_id={doc_id}"}


def list_collections(config: dict) -> dict:
    """列出所有 collections"""
    client = get_client(config)
    try:
        collections = client.get_collections()
        return {"success": True, "collections": [c.name for c in collections.collections]}
    except Exception as e:
        return {"success": False, "message": str(e)}