# CIP-Core Examples

Reference implementations demonstrating CIP v2 integration patterns.

## Examples

### [research-amplifier](research-amplifier/)

**AI-Powered Social Media for Research Communication**

A complete application demonstrating:
- **Knowledge Graph**: CIP v2 semantic organization of research concepts
- **Mitosis**: Dynamic context assembly for LLM consumption
- **Progressive-Critical Agents**: Generate → Critique → Refine pipeline
- **Platform Integration**: Twitter/LinkedIn post generation

**Use as:**
- Reference implementation for CIP-based applications
- Starting point for your own research communication tools
- Portfolio example of modern Python architecture

```bash
# Install and run
cd examples/research-amplifier
pip install -e .
amplify init
amplify status
```

## Adding New Examples

Each example should:
1. Have its own `pyproject.toml` for standalone installation
2. Demonstrate a specific CIP integration pattern
3. Include clear documentation and usage examples
4. Be self-contained but reference cip-core as a dependency

## Structure

```
examples/
├── research-amplifier/     # Social media automation
│   ├── src/               # Source code
│   ├── examples/          # Sample configs
│   └── pyproject.toml     # Standalone package
└── [future-examples]/
```
