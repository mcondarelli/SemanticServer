import os
from pathlib import Path
from pydantic import BaseModel
import yaml


class Settings(BaseModel):
    embedding_model: str = "all-MiniLM-L6-v2"
    persist_dir: str = "data/chroma_db"
    top_k: int = 5


def load_config(path: str = None) -> Settings:
    if path is None:
        path = os.getenv("SEMANTIC_CONFIG", "config.yaml")
    config_path = Path(path)
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return Settings(**data)
    else:
        return Settings()
