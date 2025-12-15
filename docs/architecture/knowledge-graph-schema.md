# Knowledge Graph Schema

**Version:** 2.0.0  
**Status:** Draft  
**Module:** `cip_core.knowledge_graph`

---

## Overview

The Knowledge Graph is the semantic backbone of CIP v2, organizing research knowledge into:
- **Concepts**: Documented ideas with relationships
- **Entries**: Human-curated research events (triggers for social posts)
- **Relationships**: How concepts connect to each other

---

## Directory Structure

```
repository/
└── cip/
    ├── knowledge-graph.yaml     # Master index (required)
    ├── concepts/                # Concept documentation (required)
    │   ├── pac-theory.md
    │   ├── quantum-validation.md
    │   └── field-dynamics.md
    ├── entries/                 # Research events (required)
    │   ├── 2024-12-11-quantum-corrections.json
    │   └── 2024-12-08-prime-patterns.json
    ├── embeddings/              # Vector DB (optional, auto-generated)
    │   └── concepts.db
    └── schema/                  # Validation schemas (optional)
        ├── concept.schema.json
        └── entry.schema.json
```

---

## knowledge-graph.yaml Schema

```yaml
# knowledge-graph.yaml
# Master index for the CIP v2 Knowledge Graph

metadata:
  schema_version: "2.0.0"
  project: "dawn-field-theory"
  description: "Dawn Field Theory research knowledge graph"
  updated: "2024-12-11T00:00:00Z"

# Concept definitions
concepts:
  pac_theory:
    id: "pac_theory"
    type: "foundational"           # foundational | experimental | meta | tooling
    status: "stable"               # draft | active | stable | deprecated
    definition: "Potential Actualization Conservation principle - energy conservation generalized to information"
    files:
      - path: "concepts/pac-theory.md"
        type: "overview"           # overview | technical | examples | history
    tags:
      - "core"
      - "conservation"
      - "information"
    relates_to:
      - "field_dynamics"
      - "quantum_validation"

  field_dynamics:
    id: "field_dynamics"
    type: "foundational"
    status: "active"
    definition: "Mathematical framework for field evolution and interactions"
    files:
      - path: "concepts/field-dynamics.md"
        type: "overview"
      - path: "concepts/field-dynamics-math.md"
        type: "technical"
    tags:
      - "core"
      - "mathematics"
    relates_to:
      - "pac_theory"
      - "quantum_validation"

  quantum_validation:
    id: "quantum_validation"
    type: "experimental"
    status: "active"
    definition: "Validating quantum mechanical predictions from field dynamics"
    significance: "HIGH"           # LOW | MEDIUM | HIGH | CRITICAL
    files:
      - path: "concepts/quantum-validation.md"
        type: "overview"
    tags:
      - "validation"
      - "quantum"
      - "experiments"
    relates_to:
      - "field_dynamics"
      - "pac_theory"

# Explicit relationship definitions (optional, supplements relates_to)
relationships:
  - source: "quantum_validation"
    target: "field_dynamics"
    type: "validates"              # validates | extends | depends_on | contradicts | implements
    strength: 1.0                  # 0.0 - 1.0
    description: "QV validates predictions from FD"

  - source: "pac_theory"
    target: "field_dynamics"
    type: "constrains"
    strength: 0.9
    description: "PAC provides conservation constraints for FD"

# Graph metadata
graph_stats:
  total_concepts: 3
  total_relationships: 2
  last_validation: "2024-12-11T00:00:00Z"
```

---

## Concept Document Template

```markdown
# [Concept Name]

**ID:** concept_id  
**Type:** foundational | experimental | meta | tooling  
**Status:** draft | active | stable | deprecated  
**Last Updated:** YYYY-MM-DD

## Definition

One paragraph definition accessible to general audience.

## Technical Description

Detailed technical explanation for experts.

## Key Results

- Result 1
- Result 2

## Relationships

- **Validates:** [other_concept]
- **Depends on:** [another_concept]

## References

- Internal: [link to paper/experiment]
- External: [citation]

## Tags

`tag1`, `tag2`, `tag3`
```

---

## Entry Schema

See [entry-schema.md](entry-schema.md) for full specification.

### Quick Reference

```json
{
  "entry_id": "2024-12-11-quantum-corrections",
  "timestamp": "2024-12-11T23:45:00Z",
  "type": "validation_result",
  
  "summary": {
    "technical": "Added second-order corrections to QHO derivation. 6 decimal agreement with QM.",
    "accessible": "Quantum predictions now match experiments perfectly.",
    "one_liner": "Quantum from fields: 6 decimals precision"
  },
  
  "significance": {
    "level": "HIGH",
    "reasoning": "Proves field dynamics captures quantum behavior",
    "connects_to": ["quantum_validation", "field_dynamics"]
  },
  
  "post_guidance": {
    "angle": "Precision milestone",
    "hooks": ["QM without wave equations", "Theory meets experiment"],
    "avoid": "Don't oversell - one system only",
    "suggested_tone": "thoughtful"
  },
  
  "meta": {
    "created_by": "Peter",
    "posted": false,
    "post_ids": []
  }
}
```

---

## Validation Rules

### Knowledge Graph
1. All concept IDs must be unique
2. All `relates_to` references must exist
3. All file paths must resolve
4. Schema version must be supported

### Concepts
1. Required fields: id, type, definition, files
2. At least one file must exist
3. Tags must be lowercase, hyphenated

### Entries
1. Required fields: entry_id, timestamp, type, summary, significance
2. All `connects_to` concept IDs must exist
3. Timestamp must be ISO 8601

---

## Python API

```python
from cip_core.knowledge_graph import KnowledgeGraph

# Load knowledge graph
kg = KnowledgeGraph("/path/to/repo")

# Get concept
concept = kg.get_concept("quantum_validation")
print(concept.definition)
print(concept.files)

# Find related concepts
related = kg.get_related("quantum_validation", depth=1)
# Returns: ['field_dynamics', 'pac_theory']

# Search concepts
results = kg.search("quantum", limit=5)
# Returns: [('quantum_validation', 0.95), ('field_dynamics', 0.3)]

# Get unposted entries
entries = kg.get_entries(days=7, unposted_only=True)

# Update entry status
kg.mark_posted("2024-12-11-quantum-corrections", post_id="tw_123")
```

---

## CLI Commands

```bash
# Initialize knowledge graph in repository
cip kg init

# Add concept interactively
cip kg add-concept

# Add entry from commits
cip kg add-entry --commits abc123 def456

# Validate knowledge graph
cip kg validate

# Search concepts
cip kg search "quantum validation"

# Export for agents
cip kg export --format json --output kg_export.json
```

---

## Migration from CIP v1

Existing `meta.yaml` files can coexist with the knowledge graph. The migration path:

1. Create `cip/knowledge-graph.yaml` with initial concepts
2. Document concepts in `cip/concepts/`
3. Create entries for recent significant work
4. Gradually reference KG from existing meta.yaml files

```yaml
# meta.yaml can reference KG concepts
cip_knowledge_graph:
  primary_concepts:
    - "quantum_validation"
    - "field_dynamics"
```
