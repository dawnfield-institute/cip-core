# 🔧 Scripts & Automation

> **Documentation for CIP automation scripts and integration tools**

This section documents the scripts and automation tools that make CIP easier to use in different environments and workflows.

---

## 📖 **Available Scripts**

### **🚀 Initialization Scripts**
- **[`initialization.md`](initialization.md)** - Repository setup and initialization scripts
  - `repo-init.ps1` (Windows PowerShell)
  - `repo-init.sh` (Linux/Mac bash)  
  - `quick-setup.py` (Cross-platform Python)

### **🔧 Maintenance Scripts**
- **[`maintenance.md`](maintenance.md)** - Ongoing maintenance and updates
  - `validate-all.ps1` - Batch validation across projects
  - `update-metadata.sh` - Refresh all metadata
  - `health-check.py` - Repository health assessment

### **🔗 Integration Scripts**
- **[`integration.md`](integration.md)** - CI/CD and workflow integration
  - GitHub Actions templates
  - VS Code integration scripts
  - Docker container helpers

---

## 🎯 **Quick Usage Examples**

### **Initialize a New Repository**
```powershell
# Windows PowerShell
.\scripts\init\repo-init.ps1 -Type theory -AIProvider ollama

# Linux/Mac bash  
./scripts/init/repo-init.sh --type theory --ai-provider ollama

# Cross-platform Python
python scripts/init/quick-setup.py --type theory --ai-provider ollama
```

### **Batch Maintenance**
```powershell
# Validate all repositories in a workspace
.\scripts\maintenance\validate-all.ps1 -WorkspacePath "C:\repos"

# Update metadata for all repos
./scripts/maintenance/update-metadata.sh /home/user/repos
```

### **CI/CD Integration**
```yaml
# .github/workflows/cip-validation.yml
name: CIP Validation
on: [push, pull_request]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: ./scripts/github-actions/cip-validate
```

---

## 📁 **Script Organization**

### **Planned Script Structure**
```bash
scripts/
├── init/                          # Repository initialization
│   ├── repo-init.ps1             # Windows PowerShell script
│   ├── repo-init.sh              # Linux/Mac bash script
│   ├── quick-setup.py            # Cross-platform Python
│   └── templates/                # Repository templates
│       ├── theory-repo/
│       ├── sdk-repo/
│       └── protocol-repo/
├── maintenance/                   # Ongoing maintenance
│   ├── validate-all.ps1          # Batch validation
│   ├── update-metadata.sh        # Metadata refresh
│   ├── health-check.py           # Health assessment
│   └── cleanup-legacy.py         # Remove deprecated files
├── integration/                   # CI/CD and workflow integration
│   ├── github-actions/           # GitHub Actions templates
│   │   ├── cip-validate.yml
│   │   ├── auto-metadata.yml
│   │   └── release-check.yml
│   ├── vscode/                   # VS Code integration
│   │   ├── settings.json
│   │   ├── tasks.json
│   │   └── extensions.json
│   └── docker/                   # Container helpers
│       ├── Dockerfile.cip
│       └── docker-compose.cip.yml
└── examples/                     # Example usage scripts
    ├── batch-processing/
    ├── custom-workflows/
    └── troubleshooting/
```

---

## 🛠️ **Development Status**

### **🚧 In Development**
- Repository initialization scripts
- Cross-platform compatibility
- Template system for different repo types

### **📋 Planned**
- Batch processing tools
- Advanced CI/CD integration
- Docker containerization helpers
- VS Code extension integration

### **💭 Ideas for Future**
- Web-based setup wizard
- GUI configuration tools
- Plugin system for custom scripts
- Integration with popular dev tools

---

## 🎯 **Design Principles**

### **1. Cross-Platform Compatibility**
- PowerShell for Windows users
- Bash for Linux/Mac users
- Python for universal compatibility

### **2. Template-Driven**
- Repository type detection
- Customizable templates
- Consistent structure across projects

### **3. Integration-Friendly**
- CI/CD pipeline support
- IDE integration
- Container-ready workflows

### **4. User-Friendly**
- Clear prompts and feedback
- Helpful error messages
- Dry-run options for safety

---

## 🔗 **Related Documentation**

- **Getting started**: [`../user-guide/installation.md`](../user-guide/installation.md)
- **Repository setup**: [`../examples/repository-setup/`](../examples/repository-setup/)
- **Architecture**: [`../architecture/core-design.md`](../architecture/core-design.md)
- **Contributing**: [`../developer-guide/contributing.md`](../developer-guide/contributing.md)
