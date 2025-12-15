# CIP Server

REST API server for Cognition Index Protocol (CIP) - provides semantic search, validation, and navigation for CIP-structured repositories.

## Quick Start

1. **Install Dependencies**:
```bash
pip install -r requirements.txt
```

2. **Create Config** (optional):
```bash
cp config/server.example.yaml config/server.yaml
# Edit config/server.yaml if needed
```

3. **Run Server**:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

4. **Test It**:
```bash
python test_server.py
```

## Architecture

```
server/
├── main.py              # FastAPI application entry point
├── config.py            # Configuration management
├── api/                 # REST API endpoints
│   ├── graph.py         # Knowledge graph queries
│   ├── index.py         # Repository indexing
│   ├── validate.py      # CIP validation
│   ├── generate.py      # Meta.yaml generation
│   ├── nav.py           # repo:// URI navigation
│   └── score.py         # Comprehension scoring
├── services/            # Business logic layer
│   ├── graph.py         # Knowledge graph operations
│   ├── indexing.py      # Repository parsing & sync
│   ├── validation.py    # CIP validation rules
│   ├── generation.py    # LLM-powered generation
│   ├── navigation.py    # URI resolution
│   └── scoring.py       # Comprehension benchmarks
├── parsers/             # File parsers
│   ├── python.py        # Python AST parser
│   ├── markdown.py      # Markdown parser
│   └── yaml_parser.py   # YAML/meta.yaml parser
└── webhook/             # Git webhook handlers
    └── handler.py       # GitHub/GitLab/Bitbucket
```

## Features

### Knowledge Graph (`/api/graph`)
- **Semantic Search**: Find relevant code/docs by meaning
- **Concept Tracing**: Follow evolution of ideas through time
- **Relationship Navigation**: Explore connected concepts

### Repository Indexing (`/api/index`)
- **Background Workers**: Non-blocking async indexing
- **Incremental Updates**: Git webhook support
- **Multi-Parser**: Python, Markdown, YAML support

### CIP Validation (`/api/validate`)
- **Schema Validation**: meta.yaml v3.0 compliance
- **Linting**: Best practices checks
- **Batch Validation**: Check entire repos

### Navigation (`/api/nav`)
- **repo:// URIs**: Navigate with semantic paths
- **Path Resolution**: Find files by concept

## Storage Backends

### Simple Mode (Default)
- **Graph**: SQLite (no Docker needed)
- **Vectors**: ChromaDB embedded
- Good for: Development, small repos (<1000 files)

### Production Mode
- **Graph**: Neo4j (Docker recommended)
- **Vectors**: Qdrant (Docker recommended)
- Good for: Large repos, multiple repos, production

## Configuration

Edit `config/server.yaml`:

```yaml
storage:
  graph_backend: "sqlite"  # or "neo4j"
  vector_backend: "chromadb"  # or "qdrant"
  sqlite_path: "./data/cip.db"
  chromadb_path: "./data/chromadb"

llm:
  provider: "openai"  # or "anthropic", "local"
  model: "gpt-4"
  api_key_env: "OPENAI_API_KEY"

webhook:
  secret: "your-webhook-secret"
  github_enabled: true
```

## API Examples

### Index a Repository
```bash
curl -X POST http://localhost:8000/api/index/repo \
  -H "Content-Type: application/json" \
  -d '{"path": "/path/to/repo", "force": false}'
```

### Query Knowledge Graph
```bash
curl -X POST http://localhost:8000/api/graph/query \
  -H "Content-Type: application/json" \
  -d '{"query": "validation logic", "limit": 10}'
```

### Trace Concept Evolution
```bash
curl http://localhost:8000/api/graph/trace/CIPDocument
```

### Get Sync Status
```bash
curl http://localhost:8000/api/index/status/my-repo
```

## Development

### Run with Auto-Reload
```bash
uvicorn main:app --reload
```

### Test Endpoints
```bash
python test_server.py
```

### Run with Docker
```bash
docker build -t cip-server .
docker run -p 8000:8000 -v ./data:/app/data cip-server
```

## Integration

### MCP Server (Coming Soon)
The server can be wrapped with FastMCP to provide Model Context Protocol support for AI assistants.

### UI (Coming Soon)
Streamlit-based chat interface for interactive repository exploration.

## Troubleshooting

### "Graph service not available"
- Check that storage backend is configured correctly
- For Neo4j/Qdrant, ensure Docker containers are running
- Check logs: `uvicorn main:app --log-level debug`

### Indexing is slow
- Use production backends (Neo4j + Qdrant)
- Adjust batch sizes in parsers
- Check disk I/O and embeddings model

### Out of memory
- Reduce embedding model size (use 'all-MiniLM-L6-v2')
- Process fewer files per batch
- Use streaming for large files

## License

Same as cip-core parent project.
