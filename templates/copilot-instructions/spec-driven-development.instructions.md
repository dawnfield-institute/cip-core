---
applyTo: '**'
---
# Spec-Driven Development Instructions

> Load this module when working in repos with a `.spec/` directory (without CIP).

## Workflow

1. **Check for spec**: Look for `.spec/$feature.spec.md` or `.spec/$module.spec.md`
2. **Follow the spec**: Changes must align with documented design
3. **Propose spec updates**: If changes deviate, propose spec modification first
4. **Create spec for new features**: New features require specification before implementation

## .spec Directory Structure

```
.spec/
├── architecture.spec.md    # System architecture
├── $feature.spec.md        # Feature specifications
├── $module.spec.md         # Module specifications
├── guidelines.spec.md      # Project-specific rules
└── challenges.md           # Open problems/research questions
```

## Spec File Format

```markdown
# Feature Name

## Overview
Brief description of purpose

## Requirements
- [ ] Requirement 1
- [ ] Requirement 2

## Design
### Interfaces
### Data Flow
### Dependencies

## Constraints
- Performance requirements
- Compatibility requirements

## Status
- [ ] Specified
- [ ] Implemented
- [ ] Tested
- [ ] Documented
```

## Rules

### Before Implementation
- Read all relevant `.spec/*.spec.md` files
- Understand constraints and requirements
- Check `challenges.md` for open questions

### During Implementation
- Implementation must match spec
- If spec is wrong/outdated, propose update first
- Document any deviations with rationale

### When Spec Doesn't Exist
- **Stop and propose spec first** for significant features
- Small utilities/helpers may skip spec with comment explaining purpose
- Add to `challenges.md` if design decision is unclear

## Spec Updates

When proposing spec changes:
1. Quote the current spec text
2. Explain why change is needed
3. Propose new text
4. Wait for approval before implementing
