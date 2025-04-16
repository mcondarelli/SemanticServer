import os

from fastapi import FastAPI, HTTPException
from semanticserver.config import load_config
from semanticserver.embeddings.sentence_transformer import MiniLMEmbedder
from semanticserver.embeddings.chroma import Chroma

from semanticserver.models.generated import EmbedRequest, Scene, AnalysisRequest, AnalysisResult

START_DIRECTORY = os.getcwd()

app = FastAPI()
config = load_config()
embedder = MiniLMEmbedder(config.embedding_model)
chroma = Chroma(START_DIRECTORY)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/embed")
def embed_text(req: EmbedRequest):
    vector = embedder.embed(req.text)
    return {"embedding": vector}

@app.post("/scene")
def upload_scene(req: Scene):
    try:
        chroma.upload_scene(req)
        return {"status": "ok"}
    except Chroma.ChromaError as e:
        raise HTTPException(500, str(e))

@app.get("/scene/{scene_id}")
def download_scene(scene_id: str):
    try:
        return chroma.download_scene(scene_id)
    except Chroma.ChromaError as e:
        raise HTTPException(500, str(e))

@app.post("/analyze")
def analyze(req: AnalysisRequest):
    try:
        response = chroma.analyze_scene(req)
        for r in response:
            print(f'AnalyzeResult: {r}')
        if req.min_score is not None:
            response = [r for r in response.neighbors if r.similarity >= req.min_score]
        return AnalysisResult(neighbors=response)
    except Chroma.ChromaError as e:
        raise HTTPException(500, str(e))

