"""
RAG KB FastAPI 服务
提供所有 CLI 操作的 REST API，长期运行避免模块加载延迟
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from rag_kb.core import upload, upload_text, search, delete, list_all_collections
from rag_kb.config import config


app = FastAPI(title="RAG Knowledge Base API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class UploadRequest(BaseModel):
    file_path: str
    collection: str = "default"


class UploadTextRequest(BaseModel):
    text: str
    collection: str = "default"
    source: str = "api"


class SearchRequest(BaseModel):
    query: str
    collection: str = "default"
    top_k: Optional[int] = None


class DeleteRequest(BaseModel):
    doc_id: str
    collection: str = "default"


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/collections")
async def get_collections():
    result = list_all_collections()
    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("message"))
    return result


@app.post("/upload")
async def upload_file(req: UploadRequest):
    try:
        result = upload(req.file_path, req.collection)
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("message", "上传失败"))
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@app.post("/upload-text")
async def upload_text_api(req: UploadTextRequest):
    try:
        result = upload_text(req.text, req.collection, req.source)
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("message", "上传失败"))
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@app.post("/search")
async def search_api(req: SearchRequest):
    top_k = req.top_k or config.get("default_top_k", 5)
    max_top_k = config.get("max_top_k", 20)
    if top_k > max_top_k:
        top_k = max_top_k
    result = search(req.query, req.collection, top_k)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message"))
    return result


@app.post("/delete")
async def delete_api(req: DeleteRequest):
    result = delete(req.doc_id, req.collection)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message"))
    return result


def main():
    import uvicorn
    port = 8081
    print(f"启动 RAG 服务: http://localhost:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()