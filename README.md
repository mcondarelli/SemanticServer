# SemanticServer
A semantic indexing and search API for literary scenes.
Designed to support interactive and long-range editing of narrative structures by embedding text scenes and enabling contextual queries.

---

## 🚀 Features

- Scene ingestion with semantic vector embedding
- Embedding-based similarity search between scenes
- Pydantic model generation from OpenAPI YAML spec
- Optional support for GPU acceleration (CPU, CUDA, ROCm)
- Clean and modular FastAPI backend

## Status

This code is currently work-in-progress and absolutely unfit for any serious usage.

Code is bound to change dramatically as I progress my experimentation with code and models.

Since I'm interested mainly in working in Italian language my current "real life" test is 
with the Italian Constitution which is a very well-structured document, publicly available
and fre fromm any kind of copyright.

---

## 📦 Installation

### 1. Clone the repo

```bash
git clone https://github.com/mcondarelli/SemanticServer
cd SemanticServer
```

### 2. Set up your Python environment
Use provided shell script to create a suitable Python Virtual Environment and activate it. 
```bash
scripts/bootstrap.sh
source .venv/bin/activate
```
The script honours an optional argument: `rocm` to install AMD-ROCm-aware versions of 
`pythorch` ans related programs.  

### 3. Install dependencies (default: CPU-only, already included in script)
```
pip install -e .
```
Optional: Install with development tools
```
pip install -e .[dev]
```
Optional: For ROCm (AMD GPUs)
```
pip install --pre torch torchvision torchaudio \
  --index-url https://download.pytorch.org/whl/nightly/rocm6.3
pip install -e .[dev]
```
Optional: For CUDA (NVIDIA GPUs)
```
pip install torch torchvision torchaudio
pip install -e .[dev]
```
## 🧪 Usage
Start the server:
```
uvicorn semanticserver.main:app --reload --app-dir src
```
### Available endpoints:

-    GET /health — Health check
-    POST /embed — Return embedding vector from text
-    POST /scene — Add or update a scene
-    POST /analyze — Get semantically similar scenes

#### Interactive docs:
- 📘 Swagger UI → http://localhost:8000/docs
- 📘 Redoc → http://localhost:8000/redoc
- 🧱 Project Structure
```
SemanticServer/
├── data                    # Runtime persistence (excluded from git)
│   └── chroma_db
├── openapi.yaml            # API spec (used to generate models)
├── pyproject.toml          # Install config and dependency groups
├── README.md
├── scripts
│   ├── bootstrap.py        # One-time generation of pydantic models
│   └── bootstrap.sh        # One-time generation of .vnv
├── setup.py
├── src                     # Bootstrap + model generation
│   └── semanticserver
│       ├── config.py
│       ├── embeddings
│       │   ├── base.py
│       │   ├── chroma.py
│       │   └── sentence_transformer.py
│       ├── __init__.py
│       ├── main.py
│       └── models
│           ├── generated.py
│           └── id_gen.py
└── test
    ├── fetch_constitution.py
    ├── test_client.py
    └── test_query.py
```
## 🛠 Requirements

    Python 3.9+

    pip, setuptools, wheel

## 📄 License
GPLv3 License

## 📌 Notes

    This project is under active development.

    GPU acceleration is optional and handled via optional dependency groups.

    Scene metadata, extractors, and persistence logic are modular and extensible.

    For testing purposes a `SemanticServer/data` directory will b created to hold
    `chroma_db` and other persistency files.

## 🤝 Contributing

Contributions, questions, or feedback are welcome.

This project uses openapi.yaml as the source of truth for its API and generates 
models automatically during setup.



