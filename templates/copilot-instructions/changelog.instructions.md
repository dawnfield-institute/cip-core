---
applyTo: '**'
---
# Changelog Instructions

> **NEVER create summary markdown files.** Use the changelog folder instead.

## Changelog Structure

```
.changelog/
├── README.md                           # Optional: changelog overview
└── YYYYMMDD_HHMMSS_brief_slug.md      # One file per session
```

## Filename Format

```
YYYYMMDD_HHMMSS_brief_description.md
```

Examples:
- `20251229_120300_zenodo_uploads_complete.md`
- `20251229_143000_modular_instructions_refactor.md`
- `20251228_091500_pac_validation_experiment.md`

## Entry Template

```markdown
# [Brief Title]

**Date**: YYYY-MM-DD HH:MM
**Commit**: [hash] (if applicable)
**Type**: engineering | research | documentation | refactor | bugfix | release

## Summary
One paragraph overview of what was accomplished.

## Changes

### Added
- New files, features, or capabilities

### Changed
- Modifications to existing functionality

### Fixed
- Bug fixes or corrections

### Removed
- Deleted files or deprecated features

## Details
Extended notes, reasoning, discoveries, or technical decisions worth preserving.
Include links to relevant files, DOIs, or external resources.

## Related
- Links to related changelog entries, issues, or documents
```

## Rules

1. **One file per session** with meaningful changes
2. **Timestamp in filename** for chronological sorting
3. **Include commit hash** when changes are committed
4. **Type tag** for filtering (engineering/research/documentation/etc.)
5. **Keep summaries actionable** - what was done, not what will be done
6. **Link to artifacts** - DOIs, files, external resources
7. **Preserve reasoning** - why decisions were made, not just what

## When to Create an Entry

Create a changelog entry when:
- Completing a meaningful unit of work
- Making commits that affect functionality
- Finishing research experiments
- Publishing or uploading artifacts
- Making architectural decisions
- Resolving significant issues

Do NOT create entries for:
- Trivial typo fixes
- Work-in-progress that isn't committed
- Exploratory work that led nowhere (unless the learning is valuable)

## Type Definitions

| Type | Use For |
|------|---------|
| `engineering` | Code changes, implementations, infrastructure |
| `research` | Experiments, analysis, discoveries |
| `documentation` | Docs, papers, READMEs |
| `refactor` | Code restructuring without functional change |
| `bugfix` | Fixing broken functionality |
| `release` | Version releases, publications, uploads |

## Creating the Folder

If `.changelog/` doesn't exist, create it with a README:

```markdown
# Changelog

Session-based changelog for this repository.
Each file represents one work session with meaningful changes.

Files are named: `YYYYMMDD_HHMMSS_brief_description.md`

See [changelog.instructions.md] for format specification.
```
