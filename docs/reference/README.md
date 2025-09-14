# 📚 Reference Documentation

> **Quick lookup reference for schemas, validation rules, and technical specifications**

This section provides technical reference material for working with CIP - schema definitions, validation criteria, file formats, and other specifications.

---

## 📖 **Reference Material**

### **Schema Definitions**
- **[`schema-definitions.md`](schema-definitions.md)** - Complete YAML schema documentation
  - `meta.yaml` schema and validation rules
  - `map.yaml` structure requirements
  - `.cip/core.yaml` configuration schema

### **File Formats**
- **[`file-formats.md`](file-formats.md)** - CIP file format specifications
  - Metadata file structures
  - Instruction file templates
  - Validation question formats

### **Validation Rules**
- **[`validation-rules.md`](validation-rules.md)** - Complete validation criteria
  - Schema validation requirements
  - Compliance checking rules
  - Quality assessment metrics

### **AI Integration**
- **[`ai-prompts.md`](ai-prompts.md)** - Standard prompts and templates
  - Default generation prompts
  - Validation prompts
  - Custom prompt guidelines

### **Limitations & Constraints**
- **[`limitations.md`](limitations.md)** - Known limitations and constraints
  - Technical limitations
  - Recommended usage patterns
  - Performance considerations

---

## 🎯 **Quick Lookup Tables**

### **File Extensions & Types**
| Extension | Purpose | Required | Auto-Generated |
|-----------|---------|----------|----------------|
| `.cip/core.yaml` | Main configuration | ✅ | ✅ |
| `.cip/instructions_v*.yaml` | AI instructions | ✅ | ✅ |
| `meta.yaml` | Directory metadata | ✅ | ✅ |
| `map.yaml` | Repository structure | ✅ | ✅ |
| `validation_questions.yaml` | Comprehension tests | ✅ | ✅ |
| `validation_answers.yaml` | Ground truth answers | ✅ | ❌ |

### **Repository Types**
| Type | Purpose | Key Directories | Validation Focus |
|------|---------|----------------|------------------|
| `theory` | Research repositories | `experiments/`, `theory/` | Theoretical consistency |
| `sdk` | Software packages | `src/`, `tests/`, `docs/` | Code quality, API docs |
| `protocol` | Standards & specs | `spec/`, `examples/` | Compliance, clarity |
| `project` | General projects | Variable | Basic structure |

### **AI Providers**
| Provider | Local/Remote | Models | Setup Difficulty |
|----------|--------------|--------|------------------|
| `ollama` | Local | llama2, codellama, etc. | Medium |
| `openai` | Remote | gpt-3.5, gpt-4 | Easy |
| `anthropic` | Remote | claude-3, claude-instant | Easy |
| `none` | N/A | Rule-based only | Easy |

---

## 🔧 **Configuration Examples**

### **Basic CIP Configuration**
```yaml
# .cip/core.yaml
cip_version: "4.0"
schema_version: "2.0"
metadata:
  strategy: "rule_based"
  auto_update: false
validation:
  enabled_rules: ["schema", "compliance"]
  quality_threshold: 0.7
```

### **AI-Enhanced Configuration**
```yaml
# .cip/core.yaml
cip_version: "4.0"
schema_version: "2.0"
metadata:
  strategy: "ai_enhanced"
  auto_update: true
ai_integration:
  provider: "ollama"
  model: "llama2"
  custom_prompts_dir: "prompts/"
validation:
  enabled_rules: ["schema", "compliance", "quality"]
  quality_threshold: 0.8
```

---

## 🎯 **Common Patterns**

### **Directory Metadata Pattern**
```yaml
# meta.yaml (directory level)
schema_version: 2.0
directory_name: "experiments"
description: "Active research experiments and data collection"
semantic_scope:
  - experimental_physics
  - data_analysis
files:
  - experiment_001.py
  - data_collection.md
child_directories:
  - raw_data
  - analysis_scripts
```

### **Validation Questions Pattern**
```yaml
# cognition/validation_questions.yaml
schema_version: 2.0
questions:
  - id: "purpose"
    question: "What is the primary purpose of this repository?"
    type: "comprehension"
    difficulty: "basic"
  - id: "structure"
    question: "How are experiments organized and related?"
    type: "navigation"
    difficulty: "intermediate"
```

---

## 🔗 **Related Documentation**

- **User guide**: [`../user-guide/`](../user-guide/)
- **Examples**: [`../examples/`](../examples/)
- **Architecture**: [`../architecture/`](../architecture/)
- **Developer guide**: [`../developer-guide/`](../developer-guide/)
