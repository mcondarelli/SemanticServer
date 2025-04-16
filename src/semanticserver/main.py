import os

from fastapi import FastAPI, HTTPException
from semanticserver.config import load_config
from semanticserver.embeddings.sentence_transformer import MiniLMEmbedder
from semanticserver.embeddings.semantic_db import SemanticDB

from semanticserver.models.generated import EmbedRequest, Fragment, AnalysisRequest, AnalysisResult

START_DIRECTORY = os.getcwd()

app = FastAPI()
config = load_config()
embedder = MiniLMEmbedder(config.embedding_model)
semantic_db = SemanticDB(START_DIRECTORY)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/embed")
def embed_text(req: EmbedRequest):
    vector = embedder.embed(req.text)
    return {"embedding": vector}

@app.post("/fragment")
def upload_fragment(req: Fragment):
    try:
        semantic_db.upload_fragment(req)
        return {"status": "ok"}
    except SemanticDB.SemanticDBError as e:
        raise HTTPException(500, str(e))

@app.get("/fragment/{fragment_id}")
def download_fragment(fragment_id: str):
    try:
        return semantic_db.download_fragment(fragment_id)
    except SemanticDB.SemanticDBError as e:
        raise HTTPException(500, str(e))

@app.post("/analyze")
def analyze(req: AnalysisRequest):
    try:
        response = semantic_db.analyze_fragment(req)
        for r in response:
            print(f'AnalyzeResult: {r}')
        if req.min_score is not None:
            response = [r for r in response.neighbors if r.similarity >= req.min_score]
        return AnalysisResult(neighbors=response)
    except SemanticDB.SemanticDBError as e:
        raise HTTPException(500, str(e))

