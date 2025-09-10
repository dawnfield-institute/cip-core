# 🔧 CIP-Core Technical Documentation

## 📦 Package Architecture

CIP-Core is organized into several key modules:

### Core Modules

- **`cip_core.schemas`** - YAML schema validation and generation
- **`cip_core.validators`** - Compliance checking and quality validation
- **`cip_core.automation`** - Metadata generation and workflow automation
- **`cip_core.navigation`** - Cross-repository linking and discovery
- **`cip_core.instructions`** - AI instruction generation
- **`cip_core.cli`** - Command-line interface
- **`cip_core.utils`** - Common utilities and helpers

### AI Integration Modules

- **`cip_core.ollama_local`** - Local Ollama AI integration
- **`cip_core.vm`** - Cloud VM service integration

## 🛠️ CLI Commands Reference

### Core Commands

```bash
# Initialize CIP metadata in repository
cip init --type protocol --title "My Project"

# Validate repository compliance
cip validate --path ./my-repo --format json

# Bootstrap complete CIP automation
cip bootstrap --type sdk --path ./my-repo
```

### Metadata Generation

```bash
# Rule-based metadata generation
cip generate-metadata --force --path ./my-repo

# AI-enhanced metadata generation
cip ai-metadata --model codellama:latest --force --path ./my-repo

# Generate AI instruction files
cip generate-instructions --validate --path ./my-repo
```

### Repository Navigation

```bash
# Resolve repo:// URLs
cip resolve "repo://dawn-field-theory/foundational/entropy_collapse.md"

# List ecosystem repositories
cip list-repos --ecosystem-root ../

# Validate cross-repository links
cip validate-links --repository my-repo
```

### AI Enhancement

```bash
# Test AI integration
cip ai-enhance --test-only --model codellama:latest

# Full repository AI enhancement
cip ai-enhance --force --model codellama:latest --path ./my-repo
```

### VM Service Commands

```bash
# Trigger cloud analysis
cip vm trigger --type scrutiny --model llama3.1 --repository ./my-repo

# Check VM status
cip vm status [job-id]

# List available models
cip vm models
```

## 🗄️ Schema Documentation

### Meta.yaml Schema v2.0

```yaml
schema_version: "2.0"
directory_name: "my_directory"
description: "Descriptive explanation of directory purpose and contents"
semantic_scope:
  - "primary_category"
  - "secondary_category"
  - "domain_specific_tag"
files:
  - "file1.py"
  - "README.md"
child_directories:
  - "subdirectory1"
  - "subdirectory2"

# Optional fields
proficiency_level: "intermediate"  # beginner, intermediate, advanced
estimated_context_weight: 0.75     # 0.0 to 1.0
validation_type: "automated"       # manual, automated, hybrid
ai_analysis:
  model_used: "codellama:latest"
  confidence_score: 0.89
  generation_timestamp: "2025-09-10T12:00:00Z"

# Ecosystem integration
ecosystem_links:
  theory: "repo://dawn-field-theory/foundational/"
  sdk: "repo://fracton-sdk/"
  documentation: "repo://dawn-field-docs/"

# Repository-level fields (root meta.yaml only)
repository_role: "protocol"  # theory, sdk, devkit, models, protocol, infrastructure
title: "Cognition Index Protocol Core"
version: "0.1.0-dev"
license: "MIT"
```

### Instruction Files Schema

#### `.cip/instructions_v2.0.yaml`
```yaml
cip_version: "2.0"
meta_yaml_schema_version: "2.0"
description: "Usage instructions for CIP agents"
MOST_IMPORTANT:
  - "Key guidance for AI agents"
usage:
  schema_validation: "Validation instructions"
  required_fields: ["list", "of", "required", "fields"]
  optional_fields: ["list", "of", "optional", "fields"]
  navigation: "Navigation guidance"
repository_structure:
  total_directories: 25
  schema_versions_found: ["2.0"]
  experimental_files_count: 3
  theory_documents_count: 12
  blueprint_files_count: 5
```

#### `.cip/core.yaml`
```yaml
schema_version: "2.0"
orientation_type: "directory_index"
description: "Directory-level orientation index for CIP navigation"
generated_date: "2025-09-10"
primary_directories:
  directory_name:
    semantic_scope: ["scope", "tags"]
    file_count: 10
    schema_version: "2.0"
document_categories:
  theory: ["list", "of", "directories"]
  experiments: ["list", "of", "directories"]
  blueprints: ["list", "of", "directories"]
  tools: ["list", "of", "directories"]
navigation_hints:
  foundational_theory: "foundational/"
  experiments: "experiments/ and blueprints/"
  tools_utilities: "tools/ and devkit/"
```

## 🔗 Integration Guide

### Adding CIP to Existing Projects

1. **Install CIP-Core**:
   ```bash
   pip install cip-core
   ```

2. **Initialize CIP metadata**:
   ```bash
   cd your-project
   cip init --type sdk --title "Your Project Name"
   ```

3. **Generate directory metadata**:
   ```bash
   cip ai-metadata --force
   ```

4. **Generate AI instructions**:
   ```bash
   cip generate-instructions --validate
   ```

5. **Validate compliance**:
   ```bash
   cip validate
   ```

### Ecosystem Integration

Link your repository to the Dawn Field Theory ecosystem:

```yaml
# In your .cip/meta.yaml
ecosystem_links:
  theory: "repo://dawn-field-theory/foundational/"
  protocols: "repo://cip-core/"
  documentation: "repo://your-docs-repo/"
```

### Custom Validation Rules

```python
from cip_core.validators import ComplianceValidator

# Custom validation configuration
config = {
    "rules": {
        "require_meta_yaml": True,
        "require_readme": True,
        "require_license": False,  # Optional for internal projects
        "validate_ecosystem_links": True,
        "check_filename_conventions": False
    }
}

validator = ComplianceValidator(config)
report = validator.validate_repository("./my-repo")
```

## 🚀 Performance Considerations

### AI Enhancement Performance

- **Local Ollama**: ~2-5 seconds per directory
- **Cloud VM**: ~1-2 seconds per directory (with GPU acceleration)
- **Batch Processing**: Processes directories in parallel when possible

### Memory Usage

- **Small repos** (<50 directories): <100MB RAM
- **Large repos** (>500 directories): <500MB RAM
- **VM Service**: Scales automatically based on load

### Scalability

- **Repository size**: Tested up to 1000+ directories
- **Cross-repo linking**: Supports unlimited ecosystem size
- **Concurrent validation**: Thread-safe for parallel processing

---

*For implementation examples, see the case studies in `../case_studies/`*
