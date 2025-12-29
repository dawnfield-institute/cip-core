---
applyTo: '**'
---
# CIP Navigation Instructions

> Load this module when working in repos with a `.cip/` directory.
> CIP (Cognition Index Protocol) takes precedence over `.spec`.

## Navigation Flow

```
.cip/instructions_v*.yaml → map.yaml → target directory meta.yaml → referenced files
```

## Step-by-Step Navigation

1. **Read `.cip/instructions_v*.yaml`**: Start here for schema version and parsing rules
2. **Read `.cip/core.yaml`**: Understand core directories and orientation
3. **Read `.cip/meta.yaml`**: Get CIP configuration metadata
4. **Check `.cip/guidelines/`**: Review any guidelines (e.g., `GenerationHumilityGuidelines.md`)
5. **Use `map.yaml`**: Canonical source of truth for repository structure and paths
6. **Check `meta.yaml` in directories**: Each directory has its own meta.yaml

## meta.yaml Structure

Each directory's meta.yaml contains:
```yaml
schema_version: "2.0"
description: "What this folder contains"
semantic_scope: "implementation|documentation|data|publication"
files:
  - "[filename.ext]": "Brief description"
child_directories:
  - name: "subdir"
    description: "What it contains"
proficiency_level: "research|production|experimental"
estimated_context_weight: 0.1-1.0
validation_type: "manual|automated|none"
```

## Key Rules

- **Ingest documents fully** before forming opinions (metadata alone is insufficient)
- **Use `map.yaml`** to resolve all paths (never infer from relative paths)
- **Only bracket-tagged files** in meta.yaml are canonical intellectual artifacts
- **Check `INTENTIONS.md`** and `timeline.md` for project goals and status
- **Apply guidelines** from `.cip/guidelines/` for tone, rigor, and approach

## CIP vs .spec Priority

| Scenario | Action |
|----------|--------|
| Repo has `.cip/` | CIP takes precedence |
| Repo has `.spec/` only | Follow spec-driven-development module |
| Repo has both | CIP for navigation, `.spec` for design constraints |
| Research model (e.g., GAIA) | Both apply - see experiment-schema module |
