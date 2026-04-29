"""
CLI
"""
import json
import argparse
from .core import upload, upload_text, search, delete, list_all_collections
from .config import config


def run_cli():
    parser = argparse.ArgumentParser(description="RAG CLI")
    sub = parser.add_subparsers(dest="cmd")

    default_collection = config.get("default_collection", "default")
    default_top_k = config.get("default_top_k", 5)

    sub.add_parser("list", help="列出 collections")
    p = sub.add_parser("search", help="检索")
    p.add_argument("query")
    p.add_argument("-c", "--collection", default=default_collection)
    p.add_argument("-k", "--top-k", type=int, default=default_top_k)
    p = sub.add_parser("upload-text", help="上传文本")
    p.add_argument("text")
    p.add_argument("-c", "--collection", default=default_collection)
    p = sub.add_parser("upload", help="上传文件")
    p.add_argument("file")
    p.add_argument("-c", "--collection", default=default_collection)
    p = sub.add_parser("delete", help="删除")
    p.add_argument("doc_id")
    p.add_argument("-c", "--collection", default=default_collection)

    args = parser.parse_args()
    if not args.cmd:
        parser.print_help()
        return

    if args.cmd == "list":
        result = list_all_collections()
    elif args.cmd == "search":
        result = search(args.query, args.collection, args.top_k)
    elif args.cmd == "upload-text":
        result = upload_text(args.text, args.collection)
    elif args.cmd == "upload":
        result = upload(args.file, args.collection)
    elif args.cmd == "delete":
        result = delete(args.doc_id, args.collection)
    else:
        parser.print_help()
        return

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    run_cli()
