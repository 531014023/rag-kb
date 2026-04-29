"""
配置模块
"""
import os
import yaml
from pathlib import Path

# 查找项目根目录（config.yaml 所在位置）
# 优先使用环境变量，其次向上查找
def find_project_root():
    # 环境变量指定
    env_path = os.environ.get("RAG_KB_CONFIG")
    if env_path:
        p = Path(env_path)
        if p.exists():
            return p.parent
        p = Path(env_path).parent
        if (p / "config.yaml").exists():
            return p

    # 向上查找
    current = Path(__file__).parent  # src/rag_kb/
    for parent in [current.parent, current.parent.parent, current.parent.parent.parent]:
        if (parent / "config.yaml").exists():
            return parent
    return current.parent.parent  # 回退到 src/


PROJECT_ROOT = find_project_root()
CONFIG_PATH = PROJECT_ROOT / "config.yaml"


def load_config() -> dict:
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    return {}


config = load_config()