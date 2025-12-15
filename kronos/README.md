# Kronos

**Fractal Graph Memory for Repository Understanding**

> Ported from GRIMM's Kronos memory system, adapted for CIP repository knowledge graphs.

## Overview

Kronos provides a GPU-accelerated knowledge graph combining:
- **Vector DB** (Qdrant/ChromaDB) for semantic similarity
- **Graph DB** (Neo4j/SQLite) for relationships
- **PyTorch** for GPU acceleration
- **Fractal signatures** for unique identity

## Installation

```bash
# From cip-core root
pip install -e ./kronos

# Or standalone
cd kronos
pip install -e .
```

## Quick Start

```python
from kronos import KronosStorage, NodeType, RelationType

# Initialize storage
storage = KronosStorage(
    graph_backend="sqlite",  # or "neo4j"
    vector_backend="chromadb",  # or "qdrant"
    device="cpu"  # or "cuda"
)

# Store a file node
node_id = await storage.store_node(
    content="def hello(): print('world')",
    node_type=NodeType.FUNCTION,
    metadata={"path": "src/hello.py", "name": "hello"}
)

# Create relationship
await storage.create_edge(
    from_id=node_id,
    to_id=parent_file_id,
    relation=RelationType.PART_OF
)

# Semantic query
results = await storage.query("function that prints hello")
```

## Architecture

```
kronos/
├── __init__.py           # Public API
├── types.py              # Core types (Node, Edge, enums)
├── storage.py            # Unified storage interface
├── graph/                # Graph backends
│   ├── __init__.py
│   ├── base.py           # Abstract interface
│   ├── neo4j.py          # Neo4j implementation
│   └── sqlite.py         # SQLite implementation
├── vectors/              # Vector backends
│   ├── __init__.py
│   ├── base.py           # Abstract interface
│   ├── qdrant.py         # Qdrant implementation
│   └── chromadb.py       # ChromaDB implementation
├── embeddings.py         # Embedding generation
└── navigation.py         # Graph traversal & ranking
```

## Node Types (for repositories)

| Type | Description |
|------|-------------|
| `FILE` | Source file |
| `DIRECTORY` | Folder |
| `FUNCTION` | Function/method |
| `CLASS` | Class definition |
| `MODULE` | Module/package |
| `CONCEPT` | Abstract concept |
| `DOCUMENT` | Documentation |
| `COMMIT` | Git commit |

## Relationship Types

| Type | Description |
|------|-------------|
| `CONTAINS` | Parent-child |
| `PART_OF` | Child-parent |
| `IMPORTS` | Import dependency |
| `CALLS` | Function call |
| `EVOLVES_FROM` | Temporal evolution |
| `RELATES_TO` | Semantic relation |
| `SUPPORTS` | Supporting evidence |
| `CONTRADICTS` | Conflicting info |

## Origin

Ported from: `grimm/apps/core/memory/kronos/`

The original Kronos was designed for GRIMM's cognitive memory. This version adapts the fractal graph architecture for repository understanding while maintaining the core concepts:

- **SEC-based ranking** - Symbolic Entropy Collapse for resonance
- **Fractal signatures** - Unique node identity
- **GPU acceleration** - PyTorch tensor operations
- **Temporal tracking** - EVOLVES_FROM edges

## License

MIT (same as cip-core)
