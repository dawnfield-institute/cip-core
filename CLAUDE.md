# CIP-Core -- Claude Code Context

## Identity
CIP-Core is the foundational implementation of the Cognition Index Protocol (CIP) -- AI-enhanced repository automation for scientific computing. Provides intelligent metadata generation (via Ollama), schema validation, cross-repository navigation with `repo://` URLs, and a CLI toolkit. Version 0.1.0-dev, MIT licensed. Part of the Dawn Field Theory ecosystem.

## Architecture

```
cip-core/
├── cip_core/                # Core Python package
│   ├── cli/                 # Command-line interface (cip command)
│   ├── schemas/             # YAML schema validation
│   ├── validators/          # Compliance checking
│   ├── automation/          # AI-enhanced metadata generation
│   ├── navigation/          # Cross-repository linking (repo:// URLs)
│   ├── instructions/        # AI instruction generation
│   ├── ollama_local/        # Local Ollama AI integration
│   ├── engine/              # Core CIP engine
│   ├── generation/          # Metadata generation
│   ├── validation/          # Validation logic
│   ├── vm/                  # Cloud VM service integration
│   └── utils/               # Common utilities
├── kronos/                  # KRONOS sub-package
│   ├── kronos/              # Knowledge graph operations
│   └── tests/               # KRONOS tests
├── server/                  # CIP server (REST API)
│   ├── api/                 # API endpoints
│   ├── services/            # Business logic
│   ├── parsers/             # Input parsers
│   ├── webhook/             # Webhook handlers
│   └── config.py            # Server configuration
├── tests/                   # Test suite (validators, schemas, CLI, etc.)
├── config/                  # Configuration files
├── templates/               # CIP configuration templates
├── docs/                    # Documentation (architecture, technical, GPT guides)
├── roadmap/                 # Development planning
└── .cip/                    # CIP protocol self-configuration (meta.yaml, core.yaml)
```

## Key APIs / CLI

**CLI Commands**: `cip init`, `cip validate`, `cip bootstrap`, `cip ai-metadata`, `cip ai-enhance`, `cip generate-instructions`, `cip resolve`, `cip list-repos`, `cip validate-links`
**Core Modules**: Schema validation, compliance checking, AI metadata generation, repo:// URL resolution
**Server**: REST API for CIP operations, webhook handlers, parser services
**KRONOS**: Knowledge graph sub-package for graph operations

## Conventions

- Install: `pip install -e .` (provides the `cip` CLI command)
- Alternative: `python -m cip_core.cli.main` without installation
- Tests: `pytest tests/` from repo root
- CIP metadata lives in `.cip/` directory (meta.yaml, core.yaml)
- AI features require local Ollama instance running
- Server: `python server/main.py`

## Related Repos

- `fracton` -- Infodynamics SDK (computational substrate)
- `dawn-field-theory` -- core theoretical foundation
- `reality-engine` -- physics simulation framework
- `dawn-models` -- AI model architectures
- `kronos-vault` -- knowledge vault (CIP manages its metadata)
- `dawn-devkit` -- development tools and templates

## Current State

- v0.1.0-dev, active development
- CLI operational: init, validate, bootstrap, ai-metadata all working
- Ollama AI integration functional for metadata generation
- Server component under development
- KRONOS sub-package included for knowledge graph operations

## Guardrails

- Do NOT break the CLI public interface (cip command and its subcommands)
- Do NOT modify .cip/ schema format without updating validators and schemas
- Always run `pytest tests/` after changes
- AI metadata features depend on Ollama -- handle gracefully when unavailable
- Server and cip_core are separate concerns -- keep boundaries clean
- MIT licensed -- ensure all contributions are MIT-compatible
