# Copilot Instructions Templates

Modular instruction files for GitHub Copilot. Copy these to your repo's `.github/instructions/` directory.

## Files

| File | Purpose | When to Use |
|------|---------|-------------|
| `main.instructions.md` | **Gateway** - Core principles + links | Always (main file) |
| `cip-navigation.instructions.md` | CIP protocol navigation | Repos with `.cip/` |
| `spec-driven-development.instructions.md` | Spec-driven workflow | Repos with `.spec/` |
| `zenodo-workflow.instructions.md` | Zenodo upload process | Publishing to Zenodo |
| `experiment-schema.instructions.md` | Experiments, POCs, journals | Research repos |

## Usage

### Minimal Setup
Copy only the gateway file for basic guardrails:
```
.github/instructions/
└── main.instructions.md
```

### Full Setup  
Copy all files for comprehensive coverage:
```
.github/instructions/
├── main.instructions.md
├── cip-navigation.instructions.md
├── spec-driven-development.instructions.md
├── zenodo-workflow.instructions.md
└── experiment-schema.instructions.md
```

### Project-Specific Instructions
Add a project-specific file (e.g., `dawn-field-theory.instructions.md`) for domain context.

## applyTo Header

Each file has:
```yaml
---
applyTo: '**'
---
```

This makes the instructions apply to all files. Modify for specific file patterns if needed:
- `applyTo: '*.py'` - Python files only
- `applyTo: 'src/**'` - Files in src/ directory
- `applyTo: '*.md'` - Markdown files only

## Customization

These are templates. Customize for your project:
- Add your ORCID to zenodo-workflow
- Add project-specific guidelines
- Adjust folder structures to match your conventions
