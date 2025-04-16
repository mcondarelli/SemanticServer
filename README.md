
# SemanticServer

**SemanticServer** is a modular FastAPI server and semantic storage backend designed to store and query fragments of text using semantic search and metadata-driven analysis.

It supports full-text storage, semantic embedding, and background metadata extraction for advanced querying.

---

## 🔧 Current Features

- Store and retrieve **text fragments** (formerly "scenes")
- Full text stored in a **SQLite3** backend
- Semantic embeddings indexed via **ChromaDB**
- Unified access via the `SemanticDB` class
- Background architecture for pluggable semantic processors (in progress)
- Full-text and metadata can be retrieved or updated independently

---

## 🧱 Core Concepts

### Fragment

```python
@dataclass
class Fragment:
    id: Optional[str]
    text: Optional[str]
    metadata: Optional[FragmentMetadata]
```

- A fragment represents a self-contained piece of text (e.g., a paragraph, scene, document section).
- `id` is a unique identifier (generated if missing).
- `text` is the raw content.
- `metadata` contains semantic or structural information.

### FragmentMetadata

```python
@dataclass
class FragmentMetadata:
    fields: dict[str, Any]
```

- Metadata is stored as a flexible key-value dictionary.
- Can be enriched with custom processors (e.g., extract characters, tone, summary).
- Typed properties and validation can be added incrementally.

---

## 📦 Storage Layer: `SemanticDB`

The `SemanticDB` class is the single entry point for all fragment operations.

### API

- `put_fragment(fragment: Fragment) -> Fragment`:  
  Insert or update a fragment. Missing fields are filled if possible.

- `get_fragment(fragment: Fragment, needs_text=True, needs_metadata=True, **kwargs) -> Fragment`:  
  Retrieve and complete a fragment based on its ID or other available fields. Additional retrieval options may be specified via `kwargs`.

---

## 🧠 In Progress: Semantic Pipeline

We are building a modular **semantic pipeline** that:

- Processes newly stored fragments in background
- Extracts and enriches metadata (NER, tone, summary, etc.)
- Allows multiple asynchronous processors working in parallel
- Tracks which processors have been applied via flags
- Enables queries to be aware of processing status

Processors will be manually triggerable via HTTP endpoints for testing. Future automation (e.g. cron or watch loop) will use the same endpoints.

---

## 🚀 Development Roadmap

- [x] Refactor naming (`Scene` → `Fragment`, `Chroma` → `SemanticDB`)
- [x] Full-text storage in SQLite
- [x] Unified fragment abstraction
- [ ] Background metadata processors (NER, tone, etc.)
- [ ] Modular query handlers based on metadata
- [ ] Improved embedding model selection
- [ ] Expanded semantic query API

---

## 🧪 Quickstart

```bash
# Setup
./scripts/bootstrap.sh

# Run the server
uvicorn semanticserver.main:app --reload
```

API will be available at [http://localhost:8000](http://localhost:8000)

---

## 📂 Structure Overview

```
SemanticServer/
├── src/semanticserver/
│   ├── main.py                  # FastAPI entry point
│   ├── embeddings/              # Vector store abstraction (Chroma)
│   │   └── semantic_db.py       # Unified interface (formerly chroma.py)
│   ├── models/                  # Fragment and metadata models
│   ├── semantic_pipeline_base.py # Base class for async processors
│   └── ...
├── data/                        # Runtime data (e.g. SQLite3 fulltext DB)
├── scripts/                     # Bootstrap/setup scripts
```

---

## 🧠 Philosophy

- Text fragments and metadata are first-class entities.
- Separation of concerns: storage, enrichment, and querying are modular.
- Designed for slow, background enrichment — but fast, structured querying.
- Architecture aims to support future AI-driven text analysis and classification.

---

## 📜 License

GPL3 License
