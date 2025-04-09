import time
from importlib.metadata import metadata
from pathlib import Path
from typing import Optional

from pydantic import BaseModel
import chromadb
from chromadb.utils import embedding_functions

from semanticserver.models.generated import Scene, AnalysisRequest, AnalysisResult, Neighbor


# Configuration Model
class ChromaConfig(BaseModel):
    model_name: str = "all-MiniLM-L6-v2"
    collection_name: str = "scenes"
    similarity_metric: str = "cosine"



class Chroma:
    _instance = None
    _initialized = False

    class ChromaError(Exception):
        pass

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, cwd):
        if not self._initialized:
            self._initialized = True
            self.location = Path(cwd) / 'data'
            self.config = ChromaConfig()
            self.client: Optional[chromadb.PersistentClient] = None
            self.collection: Optional[chromadb.Collection] = None
            self.last_update = 0

    def reconfigure(self, config: ChromaConfig=None):
        if config:
            self.config = config
        try:
            self.location.mkdir(parents=True, exist_ok=True)
            self.client = chromadb.PersistentClient(
                path=str(self.location / "chroma_db")
            )
            embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name=self.config.model_name
            )

            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=self.config.collection_name,
                embedding_function=embedding_func,
                metadata={"hnsw:space": self.config.similarity_metric},
            )

            self.last_update = time.time()
        except Exception as e:
            raise self.ChromaError(f"Chroma init failed: {str(e)}")

    def upload_scene(self, scene: Scene):
        if self.collection is None:
            self.reconfigure()
        metadata = {"title": scene.title, **(scene.metadata or {})}
        self.collection.upsert(
            ids=[scene.scene_id],
            documents=[scene.text],
            metadatas=[metadata]  # was: [{"title": scene.title, **scene.metadata}]
        )

    def analyze_scene(self, request: AnalysisRequest):
        if self.collection is None:
            self.reconfigure()
        res = self.collection.query(
            query_texts=[request.text],
            n_results=request.top_k
        )
        print(f'analyze_scene: {res}')
        if not res["ids"] or not res["distances"]:
            return AnalysisResult(neighbors=[])  # no results

        ids = res["ids"][0]
        distances = res["distances"][0]

        # Ensure lengths match
        if len(ids) != len(distances):
            raise ValueError("Mismatch between ids and distances in Chroma result")

        answ = AnalysisResult(neighbors=[
            Neighbor(scene_id=sid, similarity=score) for sid, score in zip(ids, distances)
        ])
        return answ

