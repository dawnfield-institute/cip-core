# 📣 Research Amplifier

**AI-Powered Social Media for Research Communication**

[![Python](https://img.shields.io/badge/python-3.11+-blue)](https://python.org)
[![CIP](https://img.shields.io/badge/CIP-v2.0-green)](../README.md)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

---

## Overview

Research Amplifier automates authentic social media presence for researchers by:

1. **Organizing knowledge** in a semantic graph (CIP v2 integration)
2. **Assembling context** via Mitosis engine
3. **Generating posts** with Progressive-Critical agent pipeline
4. **Maintaining control** through GitHub PR workflow

**Key Innovation:** Human curation + AI understanding + Agentic generation = Authentic automated presence

## Architecture

```
Research Work → Context Entry (human) → Mitosis Assembly → 
Agent Generation → Critique Loop → GitHub PR (human review) → 
Post to Platforms
```

## Installation

```bash
# From cip-core root (during incubation)
pip install -e ".[research-amplifier]"

# Or standalone (after extraction)
pip install research-amplifier
```

## Quick Start

### 1. Initialize Knowledge Graph

```bash
cd your-research-repo
amplify init
```

### 2. Add Research Entry

```bash
amplify entry create --title "Quantum corrections milestone"
```

### 3. Generate Post

```bash
amplify generate --entry 2024-12-11-quantum-corrections
```

### 4. Review & Post

PR created → Review on GitHub → Merge → Auto-posts

## Project Structure

```
research-amplifier/
├── src/research_amplifier/
│   ├── knowledge/        # CIP integration
│   ├── mitosis/          # Context assembly
│   ├── agents/           # Generation pipeline
│   ├── platforms/        # Twitter, LinkedIn
│   └── workflows/        # GitHub PR automation
├── examples/             # Sample configs & entries
├── tests/
└── docs/
```

## Configuration

```yaml
# amplifier.yaml
knowledge_graph:
  path: "cip/"
  
platforms:
  twitter:
    enabled: true
  linkedin:
    enabled: true

agents:
  model: "claude-sonnet-4-20250514"
  max_iterations: 3
  
workflow:
  pr_repo: "owner/post-review"
  auto_merge: false
```

## Development Status

🚧 **Incubating inside cip-core** - Will be extracted to standalone repo once stable.

## Links

- [Architecture](docs/architecture.md)
- [CIP Core](../README.md)
- [Roadmap](docs/roadmap.md)
