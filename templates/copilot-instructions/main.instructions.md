---
applyTo: '**'
---
# Copilot Development Guidelines

## Core Principle
**Specification-Driven Development**: Follow existing specs, propose updates when deviating.

## Instruction Modules
Load the relevant module based on task context. These are located in the same directory.

| Module | When to Load |
|--------|--------------|
| [cip-navigation.instructions.md](cip-navigation.instructions.md) | Repos with `.cip/` directory |
| [spec-driven-development.instructions.md](spec-driven-development.instructions.md) | Repos with `.spec/` directory |
| [zenodo-workflow.instructions.md](zenodo-workflow.instructions.md) | Zenodo uploads, DOI management |
| [experiment-schema.instructions.md](experiment-schema.instructions.md) | Research experiments, POCs, journals |

## Universal Rules (Always Apply)

### Architectural Guardrails
- **Do not create new files or folders** unless explicitly requested
- Work **in-place** in existing modules
- If new module/file needed, **stop and propose** with:
  - Exact path/name
  - Which layer and why
  - One-screen diff plan

### Change Management
- **Minimal impact**: Keep diffs small and focused
- **Preserve interfaces**: Don't break existing contracts
- **Protected areas**: Never modify without permission:
  - `.env*`, `*.key`, `*.pem` (secrets)
  - `.github/workflows/`, `.gitlab-ci.yml` (CI/CD)
  - `.cip/` (CIP configuration - propose changes only)
  - `*lock.json`, `*lock.yaml` (dependency locks)

### When to Stop and Ask
- Request conflicts with specs/guidelines
- Change affects >3 files
- Breaking existing interfaces
- Security/performance implications
- Architectural impact

### Validation Checklist
After changes, provide:
```
✓ Spec/CIP compliance: [which specs/meta.yaml checked]
✓ Tests: [what test files updated]
✓ Build: [command to verify]
✓ Breaking changes: [none/listed]
```
