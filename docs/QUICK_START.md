# 🚀 CIP-Core Quick Start Guide

*Get CIP-Core running in your repository in 5 minutes*

## 🎯 What is CIP-Core?

CIP-Core automatically generates intelligent documentation and metadata for your code repositories using AI. Think of it as an automated assistant that:

- 📝 **Writes meaningful descriptions** for your folders and files
- ✅ **Validates** your project structure and documentation quality  
- 🤖 **Creates AI instructions** so other AI assistants understand your code better
- 🔗 **Links repositories** together in a navigable ecosystem

## 🏃‍♂️ 30-Second Start

```bash
# 1. Install CIP-Core
pip install -e .

# 2. Initialize in your repository
cip init --type project --title "My Awesome Project"

# 3. Generate AI-enhanced descriptions
cip ai-metadata --force

# 4. Validate everything looks good
cip validate
```

**That's it!** You now have intelligent metadata throughout your repository.

## 🎨 What Just Happened?

### Step 1: `cip init`
- Created `.cip/meta.yaml` with basic repository information
- Set up the foundation for CIP protocol compliance

### Step 2: `cip ai-metadata`
- Used local AI (Ollama) to analyze each directory
- Generated meaningful descriptions based on actual code content
- Replaced generic placeholder text with intelligent summaries

### Step 3: `cip validate`
- Checked that all metadata follows CIP standards
- Verified descriptions are meaningful (not generic)
- Ensured quality standards are met

## 🔍 See the Results

Check these files that were created/updated:
- `.cip/meta.yaml` - Your repository's main metadata
- `.cip/core.yaml` - Directory index with AI-generated descriptions
- `.cip/instructions_v2.0.yaml` - Instructions for AI assistants

## 🚀 Next Steps

### Option A: Basic Usage (Recommended for most users)
```bash
# Keep your metadata fresh
cip ai-metadata --update-only  # Only update changed directories
cip validate                   # Check everything is still valid
```

### Option B: Advanced Features
```bash
# Generate comprehensive AI instructions
cip generate-instructions --validate

# Set up cross-repository linking
cip resolve repo://other-project/docs/api.md

# Bootstrap complete automation workflow
cip bootstrap --type sdk
```

### Option C: Integration with Existing Tools
```bash
# Add to your CI/CD pipeline
cip validate --format json > cip-report.json

# Use in documentation generation
cip resolve repo://./README.md > project-overview.md
```

## 🆘 Troubleshooting

### "AI model not found"
```bash
# Install Ollama and pull a model
ollama pull codellama:latest
```

### "Permission denied"
```bash
# Run with appropriate permissions
sudo cip init  # or adjust file permissions
```

### "Validation failed"
```bash
# See detailed validation results
cip validate --verbose
```

## 🎓 Ready for More?

- **[Full CLI Reference](technical/README.md)** - All commands and options
- **[AI Integration Guide](gpt/how_to_use_gpt.md)** - Advanced AI features
- **[Architecture Overview](architecture/CIP_architecturev1.md)** - How CIP works under the hood

## 💡 Example Workflows

### Daily Development
```bash
# Start of day - ensure metadata is current
cip ai-metadata --update-only

# Before committing - validate compliance
cip validate
```

### Project Setup
```bash
# New project initialization
cip init --type project --title "My New Project"
cip ai-metadata --force
cip generate-instructions
git add .cip/
git commit -m "Add CIP metadata and AI instructions"
```

### CI/CD Integration
```bash
# In your GitHub Actions or similar
- name: Validate CIP Compliance
  run: |
    pip install -e .
    cip validate --format json
```

---

**🎉 Congratulations!** You're now using AI-enhanced repository automation. Your code is more discoverable, better documented, and ready for the future of AI-assisted development.
