---
applyTo: '**'
---
# Experiment Schema Instructions

> Load this module when working with research experiments, POCs, or journals.

## Experiment Folder Structure

```
experiments/
├── JOURNAL_SCHEMA.md           # Central journal specification
└── experiment_name/
    ├── meta.yaml               # Schema v2.0 experiment metadata
    ├── README.md               # Overview with key results
    ├── SYNTHESIS.md            # Cross-connections to other work
    ├── core/
    │   ├── meta.yaml
    │   └── module.py           # Reusable library code
    ├── journals/
    │   ├── meta.yaml
    │   └── YYYY-MM-DD_slug.md  # Daily research logs
    ├── papers/
    │   └── meta.yaml
    ├── results/
    │   └── meta.yaml           # Auto-generated JSON results
    └── scripts/
        ├── meta.yaml
        └── exp_NN_name.py      # Numbered experiment scripts
```

## Journal Schema

### Filename Format
```
YYYY-MM-DD_descriptive_slug.md
```

### Required Sections
```markdown
# YYYY-MM-DD: Descriptive Title

## Summary
Brief overview of day's work and outcomes.

## Timeline

### HH:MM - Activity Type
Details of what was done.

### HH:MM - Activity Type
More details.

## Key Findings
- Finding 1
- Finding 2

## Next Steps
- [ ] Task 1
- [ ] Task 2
```

### Activity Types
- **Setup** - Environment, dependencies, configuration
- **Experiment** - Running tests or simulations
- **Analysis** - Reviewing results, statistics
- **Discovery** - Unexpected findings, insights
- **Bug Fix** - Resolving issues
- **Planning** - Design decisions, roadmap

### Status Markers
| Marker | Meaning |
|--------|---------|
| ✅ | Confirmed |
| ❌ | Failed |
| 🔄 | In Progress |
| 💡 | Insight |

### Rules
- One file per day of active work
- Timestamp all activities
- Include failures (often more valuable than successes)
- Link to code and data files
- Be honest about uncertainty
- Cross-reference related experiments

## Script Naming Convention

```
exp_NN_name.py
```

Examples:
- `exp_01_baseline.py`
- `exp_02_scaling.py`
- `exp_03_falsification.py`

### Results Output
Each script saves results to:
```
results/exp_NN_name_YYYYMMDD_HHMMSS.json
```

## meta.yaml Requirements

Every directory needs a meta.yaml:
```yaml
schema_version: "2.0"
description: "What this folder contains"
semantic_scope: "implementation|documentation|data|publication"
proficiency_level: "research"
files:
  - "[filename.ext]": "Brief description"
```

---

## POC (Proof of Concept) Structure

For research models (e.g., GAIA) that combine specs with experiments:

### Folder Structure
```
proof_of_concepts/
├── meta.yaml
├── JOURNAL_SCHEMA.md
├── POC_REGISTRY.md           # Central registry of all POCs
└── poc_NNN_name/
    ├── meta.yaml
    ├── README.md             # Hypothesis, design, success criteria
    ├── journals/
    │   └── YYYY-MM-DD_slug.md
    ├── scripts/
    │   └── exp_NN_name.py
    └── results/
        └── *.json
```

### POC README Template
```markdown
# POC NNN: Name

## Hypothesis
What we're testing.

## Design
How we'll test it.

## Success Criteria
- [ ] Criterion 1 (quantified)
- [ ] Criterion 2 (quantified)

## Falsification Conditions
What would prove this wrong.

## Status
🔄 In Progress | ✅ Validated | ❌ Falsified

## Key Results
Summary of findings.
```

### POC Workflow
1. **Define in registry**: Add entry to `POC_REGISTRY.md`
2. **Create folder structure**: Use standard layout
3. **Write hypothesis**: Document in `README.md`
4. **Conduct experiments**: Log in daily journals
5. **Collect metrics**: Save to `results/`
6. **Update registry**: Mark status and key findings

### POC Registry Format
```markdown
| POC | Status | Hypothesis | Key Finding |
|-----|--------|------------|-------------|
| poc_001_name | ✅ | Brief hypothesis | Result summary |
| poc_002_name | 🔄 | Brief hypothesis | In progress |
```

---

## Research Model Navigation

For repos with both `.spec/` AND experiment folders:

### Priority Order
1. **Read `.spec/*.spec.md`**: Understand design constraints first
2. **Read `.spec/challenges.md`**: Know the open problems
3. **Check `proof_of_concepts/POC_REGISTRY.md`**: See experiment status
4. **Review `docs/theory/`**: Understand theoretical foundations
5. **Check implementation in `src/`**: Current code state

### Spec vs POC Relationship
- **Specs define what we're trying to achieve**
- **POCs explore how to achieve it**
- **POC findings may update specs**
- **Failed POCs are valuable documentation**
