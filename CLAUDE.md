# CIP-Core -- ARCHIVED

> **Status**: Archived as of 2026-02-27. Useful functionality absorbed into Kronos MCP and GRIM skills.

## What Was Absorbed

- **meta.yaml schema** → `kronos_navigate` MCP tool reads meta.yaml from any directory
- **Directory navigation** → `repo-navigate` GRIM skill replaces CIP navigation instructions
- **Directory scanning** → `kronos_search` indexes meta.yaml descriptions in BM25
- **Source context enrichment** → `kronos_deep_dive` enriches source_paths with meta.yaml metadata

## What Died

- CIP CLI (`cip init`, `cip validate`, `cip bootstrap`, etc.)
- Ollama integration for metadata generation
- Compliance scoring system
- `repo://` URL scheme (never adopted)
- `.cip/instructions_v2.0.yaml` parsing (replaced by CLAUDE.md)
- `.cip/core.yaml` orientation index (replaced by `kronos_navigate`)
- Server/REST API component

## What Remains Useful

- The 1,500+ `meta.yaml` files generated across the workspace — now consumed by Kronos MCP
- `CIP_Arithmetic_Guide` continues to use `.cip/curriculum.yaml` for its own purposes (unaffected)
- The meta.yaml schema v2.0 format (description, semantic_scope, files, child_directories) is the standard

## Original Architecture

```
cip-core/
├── cip_core/                # Core Python package
│   ├── cli/                 # Command-line interface
│   ├── schemas/             # YAML schema validation
│   ├── validators/          # Compliance checking
│   ├── automation/          # AI-enhanced metadata generation
│   ├── navigation/          # Cross-repository linking (repo:// URLs)
│   ├── ollama_local/        # Local Ollama AI integration
│   ├── engine/              # Core CIP engine
│   └── ...
├── server/                  # CIP server (REST API)
├── tests/                   # Test suite
└── .cip/                    # CIP protocol self-configuration
```
