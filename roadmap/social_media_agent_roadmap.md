# Social Media Agent Roadmap

**Status:** Specification Phase  
**Target:** Q1 2026  
**Author:** Peter Groom, Dawn Field Institute  
**Created:** December 11, 2025  
**Version:** 1.0

---

## Executive Summary

Extend CIP-Core with a **Research Automation & Social Media Agent** system that:
1. Organizes research knowledge in a semantic graph (CIP v2 Knowledge Graph)
2. Makes it agent-accessible (MCP integration)
3. Generates high-quality social media posts (Progressive-Critical Agents)
4. Maintains human control (GitHub PR workflow)

**Key Innovation:** Human curation + AI understanding + Agentic generation = Authentic automated presence

---

## Architecture Overview

```
Research Work → Context Entry (human) → MCP Query → 
Agent Generation → Critique Loop → GitHub PR (human review) → 
Post to Platforms → Analytics → Learning
```

### New CIP-Core Modules

```
cip_core/
├── knowledge_graph/           # NEW: CIP v2 Knowledge Graph
│   ├── __init__.py
│   ├── graph.py               # Knowledge graph data structures
│   ├── concepts.py            # Concept management
│   ├── relationships.py       # Relationship types and traversal
│   └── entries.py             # Research event entries
├── mitosis/                   # NEW: Context Assembly Engine
│   ├── __init__.py
│   ├── assembler.py           # Context assembly from graph
│   ├── embedding.py           # Vector embedding integration
│   └── search.py              # Semantic search
├── mcp_server/                # NEW: MCP Server Implementation
│   ├── __init__.py
│   ├── server.py              # MCP protocol server
│   ├── tools.py               # Exposed MCP tools
│   └── config.py              # Server configuration
└── agents/                    # NEW: Social Media Agents
    ├── __init__.py
    ├── context_assembly.py    # Gather relevant info
    ├── generation.py          # Create drafts (Sonnet)
    ├── critique.py            # Validate quality
    ├── personality.py         # Add character/humor
    └── github_workflow.py     # PR creation and management
```

---

## Phase 1: Knowledge Graph Foundation (Week 1-2)

### Deliverables

1. **Knowledge Graph Schema** (`cip_core/knowledge_graph/`)
   - `graph.py`: Core data structures for concepts and relationships
   - `concepts.py`: CRUD operations for concept management
   - `entries.py`: Research event entry handling

2. **Directory Structure Template**
   ```
   repository/cip/
   ├── knowledge-graph.yaml     # Master concept index
   ├── concepts/                # Detailed concept documentation
   │   └── *.md
   ├── entries/                 # Research events (human-curated)
   │   └── YYYY-MM-DD-*.json
   ├── embeddings/              # Vector database (optional v1)
   └── schema/                  # JSON schemas for validation
   ```

3. **CLI Commands**
   ```bash
   cip kg init                  # Initialize knowledge graph
   cip kg add-concept           # Add new concept
   cip kg add-entry             # Create research entry
   cip kg validate              # Validate graph integrity
   cip kg export                # Export for agents
   ```

### Success Criteria
- [ ] Knowledge graph schema validates
- [ ] Can add/retrieve concepts programmatically
- [ ] Entry creation workflow functional
- [ ] 5-7 initial concepts documented for dawn-field-theory

---

## Phase 2: Mitosis Context Assembly (Week 2)

### Deliverables

1. **Context Assembler** (`cip_core/mitosis/`)
   - Load entry and resolve related concepts
   - Traverse relationships to configurable depth
   - Assemble coherent context window

2. **Semantic Search** (simplified v1)
   - Keyword-based search across concepts
   - Tag matching and relationship following
   - (v2: ChromaDB vector embeddings)

### API Design

```python
from cip_core.mitosis import Assembler

assembler = Assembler(repo_path="/path/to/dawn-field-theory")

# Load entry with context
context = assembler.assemble_context(
    entry_id="2024-12-11-quantum-corrections",
    depth=1,                    # Related concept depth
    include_recent_entries=5,   # For continuity
    max_tokens=10000
)

# Returns:
# {
#   'entry': {...},
#   'concepts': {'concept_id': {full_content}, ...},
#   'relationships': [...],
#   'recent_entries': [...]
# }
```

### Success Criteria
- [ ] Context assembly <1s for typical entry
- [ ] Depth traversal works correctly
- [ ] Token budgeting respects limits

---

## Phase 3: MCP Server (Week 2-3)

### Deliverables

1. **MCP Server** (`cip_core/mcp_server/`)
   - Standard MCP protocol implementation
   - Tools for knowledge graph access
   - Configuration and deployment

2. **MCP Tools**
   | Tool | Description |
   |------|-------------|
   | `search_concepts(query, limit)` | Semantic search across concepts |
   | `get_concept(concept_id)` | Load full concept documentation |
   | `load_context(concept_ids, depth)` | Assemble comprehensive context |
   | `get_recent_entries(days, unposted_only)` | Fetch research events |
   | `update_entry_status(entry_id, posted)` | Mark entry as posted |

### Success Criteria
- [ ] MCP server starts and responds
- [ ] All 5 tools functional
- [ ] Response time <2s for typical queries

---

## Phase 4: Agent System (Week 3-4)

### Deliverables

1. **Agent Pipeline** (`cip_core/agents/`)
   - Context assembly agent
   - Generation agent (Claude Sonnet 4)
   - Critique agent (Progressive-Critical)
   - Personality agent (optional humor)

2. **Progressive-Critical Loop**
   ```
   Entry → Context → Generate → Critique → [Pass] → PR
                                    ↓ [Fail]
                              Revise (max 3x)
   ```

3. **GitHub Integration**
   - PR creation with post JSON
   - Comment-driven refinement
   - Merge triggers posting

### Post JSON Schema

```json
{
  "post_id": "post_2024-12-11_abc123",
  "entry_id": "2024-12-11-quantum-corrections",
  "platforms": {
    "twitter": {
      "content": "...",
      "character_count": 145
    },
    "linkedin": {
      "content": "..."
    }
  },
  "metadata": {
    "topics": ["quantum_validation"],
    "tone": "thoughtful",
    "iterations": 1
  },
  "critique_results": {
    "all_checks_passed": true
  }
}
```

### Success Criteria
- [ ] Posts match authentic voice
- [ ] Critique converges ≤3 iterations
- [ ] PR workflow functional

---

## Phase 5: Production (Week 4-5)

### Deliverables

1. **GitHub Actions Workflow**
   - Post to Twitter on PR merge
   - Post to LinkedIn on PR merge
   - Update entry status

2. **Monitoring**
   - Simple JSON logs (v1)
   - Approval rate tracking
   - Engagement metrics

3. **Documentation**
   - Quick start guide
   - Entry creation workflow
   - Agent configuration

### Success Criteria
- [ ] 90%+ human approval rate
- [ ] Reliable posting (99%+ uptime)
- [ ] Minimal manual intervention

---

## Dependencies

### External
- `anthropic` - Claude API for generation
- `chromadb` - Vector embeddings (Phase 2+)
- `PyGithub` - PR workflow
- `tweepy` - Twitter API
- `linkedin-api` - LinkedIn posting

### Internal CIP-Core
- `cip_core.schemas` - Validation
- `cip_core.navigation` - Cross-repo links
- `cip_core.cli` - Command extensions

---

## Configuration

### Environment Variables
```bash
ANTHROPIC_API_KEY=sk-ant-...
GITHUB_TOKEN=ghp_...
TWITTER_API_KEY=...
LINKEDIN_ACCESS_TOKEN=...
```

### Config File (`cip-config.yaml`)
```yaml
social_media:
  enabled: true
  max_posts_per_day: 3
  platforms:
    - twitter
    - linkedin
  
knowledge_graph:
  path: "cip/"
  embedding_model: "text-embedding-3-small"  # optional
  
agents:
  model: "claude-sonnet-4-20250514"
  max_critique_iterations: 3
  personality:
    humor_enabled: true
    technical_depth: 7  # 1-10
```

---

## Open Questions

1. **Post frequency**: 3/day vs 2-3/week?
2. **Thread support**: Design for Twitter threads from start?
3. **Image generation**: Add diagram creation to roadmap?
4. **Entry creation UX**: CLI wizard vs manual JSON?

---

## Next Actions

1. [ ] Review and approve this roadmap
2. [ ] Create knowledge-graph schema (`cip_core/knowledge_graph/`)
3. [ ] Initialize `/cip/` in `dawn-field-theory` repo
4. [ ] Document 3-5 core concepts as test data
5. [ ] Build mitosis assembler prototype

---

## Related Documents

- [CIP Protocol Roadmap](cip_protocol_roadmap.md)
- [CIP Core Design Document](../CIP_CORE_DESIGN_DOCUMENT.md)
- [Infrastructure Tools Roadmap](infrastructure_tools_roadmap.md)
