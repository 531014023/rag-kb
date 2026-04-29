"""
RAG KB CLI 入口
"""
import sys
from pathlib import Path

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from rag_kb.cli import run_cli

if __name__ == "__main__":
    run_cli()