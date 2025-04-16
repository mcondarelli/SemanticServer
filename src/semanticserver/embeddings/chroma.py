import sqlite3
import time
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


class SQLite:
    def __init__(self, file: Path):
        self.file = file
        file.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(file))
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS scenes (id TEXT PRIMARY KEY, text TEXT)''')
        self.conn.commit()

    def __del__(self):
        self.close()

    def close(self):
        if hasattr(self, 'conn') and self.conn is not None:
            self.conn.close()
            self.conn = None

    def put_scene(self, scene: Scene):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO scenes (id, text) VALUES (?, ?)", (scene.id, scene.text))
        self.conn.commit()
        self.conn.close()

    def get_scene(self, scene: Scene):
        cursor = self.conn.cursor()
        cursor.execute("SELECT text FROM scenes WHERE id = ?", (scene.id,))
        result = cursor.fetchone()
        if result:
            scene.text = result[0]
            return scene
        else:
            raise Chroma.ChromaError("Scene text not found")


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
            self.sqlite = None

    def reconfigure(self, config: ChromaConfig=None):
        if config:
            self.config = config
        try:
            if self.sqlite is not None:
                self.sqlite.close()
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
            self.sqlite = SQLite(self.location / 'auxiliary.sqlite3')
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
        self.sqlite.put_scene(scene)

    def download_scene(self, scene_id):
        scene = Scene(scene_id=scene_id, text='')
        scene = self.sqlite.get_scene(scene)
        return scene

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

