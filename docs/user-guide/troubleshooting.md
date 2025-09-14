# 🛠️ CIP-Core Troubleshooting Guide

*Quick solutions to common issues*

## 🚨 Installation Issues

### `cip: command not found`

**Cause:** CIP-Core isn't properly installed or not in PATH.

**Solution:**
```bash
# Option 1: Install in development mode
pip install -e .

# Option 2: Use direct Python execution
python -m cip_core.cli.main --version

# Option 3: Check if pip installed to correct location
which cip  # Linux/Mac
where cip  # Windows
```

### `ModuleNotFoundError: No module named 'cip_core'`

**Cause:** Package not installed or virtual environment issues.

**Solution:**
```bash
# Ensure you're in the right directory
cd cip-core/

# Install dependencies first
pip install -r requirements.txt

# Then install the package
pip install -e .
```

## 🤖 AI Integration Issues

### `No AI models found` or `Ollama connection failed`

**Cause:** Ollama not installed or no models available.

**Solution:**
```bash
# Install Ollama (if not already installed)
# Visit: https://ollama.ai/download

# Pull a recommended model
ollama pull codellama:latest

# Test Ollama is working
ollama list
```

**Alternative:** Use without AI initially
```bash
# Initialize without AI features
cip init --type project --title "My Project"

# Generate basic metadata (rule-based)
cip generate-metadata

# Add AI later when ready
cip ai-metadata --force
```

### `AI descriptions are too generic`

**Cause:** Model doesn't have enough context or using wrong model.

**Solutions:**
```bash
# Try a more capable model
ollama pull llama2:13b
cip ai-metadata --force --model llama2:13b

# Increase context for better descriptions
cip ai-metadata --force --verbose

# Use specific model for coding tasks
ollama pull codellama:latest
cip ai-metadata --force --model codellama:latest
```

## ✅ Validation Issues

### `Validation failed: Generic descriptions detected`

**Cause:** Some directories still have placeholder or generic descriptions.

**Solution:**
```bash
# See exactly which descriptions are generic
cip validate --verbose

# Regenerate AI descriptions for problem areas
cip ai-metadata --force --path ./problematic-directory/

# Or manually edit .cip/core.yaml with specific descriptions
```

### `Schema validation errors`

**Cause:** Metadata doesn't match CIP schema requirements.

**Solution:**
```bash
# Check exact schema issues
cip validate --format json

# Reinitialize if severely broken
rm -rf .cip/
cip init --type project --title "My Project"

# Common fix: Update meta.yaml format
# Check examples in docs/technical/README.md
```

## 📁 Permission Issues

### `Permission denied` errors

**Cause:** Insufficient permissions to create `.cip/` directory or files.

**Solutions:**
```bash
# Fix directory permissions
chmod 755 .
mkdir .cip
chmod 755 .cip

# Or run with appropriate permissions
sudo cip init  # Linux/Mac (use carefully)

# Windows: Run PowerShell as Administrator
```

### `Git permission issues`

**Cause:** `.cip/` directory not properly tracked in git.

**Solution:**
```bash
# Add to git tracking
git add .cip/
git commit -m "Add CIP metadata"

# Ensure .cip/ isn't in .gitignore
grep -v "\.cip" .gitignore > temp && mv temp .gitignore
```

## 🔗 Cross-Repository Issues

### `repo:// URLs not resolving`

**Cause:** Repository not properly registered or URL format incorrect.

**Solutions:**
```bash
# Check URL format
# Correct: repo://project-name/path/to/file.md
# Incorrect: repo://./local/path or repo://https://...

# List available repositories
cip list-repos

# Test resolution explicitly
cip resolve repo://target-repo/README.md --verbose
```

## 🐛 Performance Issues

### `CIP commands are very slow`

**Cause:** Large repository or AI processing overhead.

**Solutions:**
```bash
# Process incrementally (faster)
cip ai-metadata --update-only  # Only changed directories

# Exclude large directories
echo "node_modules/" >> .cipignore
echo "__pycache__/" >> .cipignore
echo ".git/" >> .cipignore

# Use faster model
ollama pull codellama:7b  # Smaller, faster model
cip ai-metadata --model codellama:7b
```

### `Out of memory errors`

**Cause:** Large files or insufficient system resources.

**Solutions:**
```bash
# Process smaller batches
cip ai-metadata --batch-size 10

# Exclude large files from processing
echo "*.zip" >> .cipignore
echo "*.tar.gz" >> .cipignore
echo "data/*.csv" >> .cipignore
```

## 🔧 Development Issues

### `Changes not reflected after editing code`

**Cause:** Package not installed in development mode.

**Solution:**
```bash
# Reinstall in development mode
pip uninstall cip-core
pip install -e .

# Or restart Python interpreter if using interactively
```

### `Import errors when extending CIP`

**Cause:** Python path or module structure issues.

**Solution:**
```bash
# Check package structure
python -c "import cip_core; print(cip_core.__file__)"

# Ensure __init__.py files exist
find cip_core/ -name "__init__.py"

# Reinstall if structure is broken
pip install -e . --force-reinstall
```

## 🆘 Getting Help

### Still stuck?

1. **Check verbose output:**
   ```bash
   cip validate --verbose
   cip ai-metadata --verbose
   ```

2. **Look at example repositories:**
   - Browse `docs/case_studies/` for working examples
   - Check `.cip/` files in this repository

3. **Common command patterns:**
   ```bash
   # Fresh start
   rm -rf .cip/ && cip init --type project
   
   # Minimal working setup
   cip init && cip generate-metadata && cip validate
   
   # Full AI setup
   cip init && cip ai-metadata --force && cip generate-instructions
   ```

4. **Check system requirements:**
   - Python 3.8+
   - Git repository
   - Ollama installed (for AI features)
   - Sufficient disk space for metadata files

### Debug Information

When reporting issues, please include:
```bash
# Version information
cip --version
python --version
ollama --version

# System information
# Linux/Mac: uname -a
# Windows: systeminfo | findstr "OS"

# Error details
cip validate --verbose 2>&1 | tee cip-debug.log
```

---

**💡 Pro Tip:** Start with the simplest setup (`cip init && cip generate-metadata`) and add AI features incrementally once basic functionality works.
