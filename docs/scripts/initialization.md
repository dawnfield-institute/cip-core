# 🚀 Repository Initialization Scripts

> **Automated setup scripts for new CIP repositories**

These scripts provide one-command setup for new repositories with CIP integration. They detect project types, configure appropriate templates, and set up AI integration.

---

## 📋 **Available Scripts**

### **Windows PowerShell** (`repo-init.ps1`)
```powershell
# Basic usage
.\repo-init.ps1 -Type theory

# With AI provider
.\repo-init.ps1 -Type sdk -AIProvider ollama -Model llama2

# Custom configuration
.\repo-init.ps1 -Type project -Title "My Web App" -Description "React app with CIP" -Force
```

### **Linux/Mac Bash** (`repo-init.sh`)
```bash
# Basic usage
./repo-init.sh --type theory

# With AI provider  
./repo-init.sh --type sdk --ai-provider ollama --model llama2

# Custom configuration
./repo-init.sh --type project --title "My Web App" --description "React app with CIP" --force
```

### **Cross-Platform Python** (`quick-setup.py`)
```python
# Command line usage
python quick-setup.py --type theory --ai-provider ollama

# Programmatic usage
from scripts.init.quick_setup import CIPInitializer

initializer = CIPInitializer()
result = initializer.setup_repository(
    repo_type="theory",
    ai_provider="ollama",
    title="Dawn Field Extensions"
)
```

---

## 🎯 **Repository Types**

### **Theory Repository**
```bash
# Example: Physics research, mathematical frameworks
./repo-init.sh --type theory
```
**Sets up:**
- Experiments directory
- Theory documentation structure
- Research-focused metadata templates
- Validation questions for theoretical concepts

### **SDK Repository**
```bash
# Example: Python packages, libraries
./repo-init.sh --type sdk
```
**Sets up:**
- Standard package structure
- API documentation templates
- Development workflow metadata
- Code quality validation

### **Protocol Repository**
```bash  
# Example: CIP itself, standards documentation
./repo-init.sh --type protocol
```
**Sets up:**
- Specification structure
- Implementation examples
- Compliance testing framework
- Reference documentation

### **Project Repository**
```bash
# Example: Web apps, general projects
./repo-init.sh --type project
```
**Sets up:**
- Basic CIP structure
- Generic metadata templates
- Flexible validation framework
- Development workflow support

---

## ⚙️ **Script Parameters**

### **Common Parameters**
```bash
--type          # Repository type (theory|sdk|protocol|project)
--title         # Repository title (auto-detected if not provided)
--description   # Repository description (AI-generated if not provided)
--ai-provider   # AI provider (ollama|openai|anthropic|none)
--model         # AI model name (provider-specific)
--force         # Overwrite existing files
--dry-run       # Show what would be done without executing
--verbose       # Detailed output
--config        # Custom config file path
```

### **PowerShell Specific**
```powershell
-Type "theory"                    # Repository type
-AIProvider "ollama"              # AI provider
-Model "llama2"                   # AI model
-Force                            # Switch parameter
-WhatIf                           # PowerShell dry-run
```

### **Bash Specific**
```bash
--type theory                     # Repository type  
--ai-provider ollama              # AI provider
--model llama2                    # AI model
--force                           # Force overwrite
--dry-run                         # Bash dry-run
```

---

## 🔄 **Script Workflow**

### **1. Detection Phase**
```bash
🔍 Analyzing repository...
  ✓ Detected Python package (setup.py found)
  ✓ Git repository initialized
  ✓ No existing CIP configuration
  📋 Recommending type: sdk
```

### **2. Template Selection**
```bash
📝 Selecting templates...
  ✓ Loading SDK template
  ✓ Configuring Python-specific metadata
  ✓ Setting up development workflow
```

### **3. AI Integration Setup**
```bash
🤖 Configuring AI integration...
  ✓ Testing Ollama connection
  ✓ Loading model: llama2
  ✓ Generating initial descriptions
```

### **4. File Generation**
```bash
📁 Creating CIP structure...
  ✓ .cip/core.yaml
  ✓ .cip/instructions_v2.0.yaml
  ✓ meta.yaml (root)
  ✓ map.yaml
  ✓ cognition/validation_questions.yaml
```

### **5. Validation**
```bash
✅ Validating setup...
  ✓ Schema validation passed
  ✓ CIP compliance verified
  ✓ AI descriptions generated
  🎉 Setup complete!
```

---

## 📋 **Example Outputs**

### **Theory Repository Setup**
```bash
$ ./repo-init.sh --type theory --title "Quantum Field Extensions"

🚀 CIP Repository Initialization
================================

🔍 Repository Analysis:
  - Path: /home/user/quantum-field-extensions
  - Type: theory (specified)
  - Git: ✓ initialized
  - Existing CIP: ✗ none found

📝 Template Configuration:
  - Using theory repository template
  - Setting up experiments/ structure
  - Configuring research metadata
  - Creating validation framework

🤖 AI Integration:
  - Provider: none (use --ai-provider to enable)
  - Manual descriptions will be used

📁 Generated Files:
  ✓ .cip/core.yaml
  ✓ .cip/instructions_v2.0.yaml  
  ✓ meta.yaml
  ✓ map.yaml
  ✓ experiments/meta.yaml
  ✓ theory/meta.yaml
  ✓ cognition/validation_questions.yaml

✅ Setup Complete!
Next steps:
  1. Review generated metadata in meta.yaml
  2. Customize cognition/validation_questions.yaml
  3. Run: cip validate
  4. Optional: cip ai-metadata (to add AI descriptions)
```

### **SDK Repository with AI**
```bash
$ ./repo-init.sh --type sdk --ai-provider ollama --model llama2

🚀 CIP Repository Initialization  
================================

🔍 Repository Analysis:
  - Path: /home/user/my-python-sdk
  - Type: sdk (specified)
  - Detected: Python package (setup.py found)
  - Git: ✓ initialized

🤖 AI Provider Setup:
  - Provider: Ollama
  - Model: llama2
  - Connection: ✓ successful
  - Testing generation: ✓ working

📝 AI-Enhanced Generation:
  - Analyzing codebase structure...
  - Generating intelligent descriptions...
  - Creating semantic metadata...

📁 Generated Files:
  ✓ .cip/core.yaml (with AI config)
  ✓ .cip/instructions_v2.0.yaml
  ✓ meta.yaml (AI-enhanced descriptions)
  ✓ map.yaml  
  ✓ src/meta.yaml (package structure)
  ✓ tests/meta.yaml (test organization)
  ✓ cognition/validation_questions.yaml

✅ Setup Complete with AI Integration!
📊 Quality Score: 8.5/10
Next steps:
  1. Review AI-generated descriptions
  2. Run: cip validate
  3. Optional: cip generate --strategy hybrid (to refine)
```

---

## 🛠️ **Customization**

### **Custom Templates**
```bash
# Use custom template directory
./repo-init.sh --type custom --template-dir ./my-templates

# Template structure:
my-templates/
├── .cip/
│   ├── core.yaml.template
│   └── instructions_v2.0.yaml.template
├── meta.yaml.template
├── map.yaml.template
└── cognition/
    └── validation_questions.yaml.template
```

### **Configuration Files**
```yaml
# custom-config.yaml
default_ai_provider: "ollama"
default_model: "llama2"
template_overrides:
  theory:
    experiments_dir: "research"
    theory_dir: "foundations"
validation:
  auto_generate_questions: true
  question_count: 15
```

### **Environment Variables**
```bash
# Set defaults via environment
export CIP_DEFAULT_AI_PROVIDER="ollama"
export CIP_DEFAULT_MODEL="llama2"
export CIP_TEMPLATE_DIR="/path/to/templates"

./repo-init.sh --type theory  # Uses environment defaults
```

---

## 🔗 **Related Documentation**

- **Repository setup examples**: [`../examples/repository-setup/`](../examples/repository-setup/)
- **Template customization**: [`../examples/repository-setup/custom-templates.md`](../examples/repository-setup/custom-templates.md)
- **AI integration**: [`../examples/ai-integration/`](../examples/ai-integration/)
- **Troubleshooting**: [`../user-guide/troubleshooting.md`](../user-guide/troubleshooting.md)
