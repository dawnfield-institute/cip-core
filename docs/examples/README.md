# 🎓 Examples & Tutorials

> **Practical guides and step-by-step tutorials for using CIP**

This section provides hands-on examples for common CIP use cases, from basic setup to advanced automation workflows.

---

## 📖 **Available Tutorials**

### **🚀 Repository Setup**
- **[`repository-setup/theory-repo.md`](repository-setup/theory-repo.md)** - Setting up research repositories
- **[`repository-setup/sdk-repo.md`](repository-setup/sdk-repo.md)** - Configuring software packages
- **[`repository-setup/project-repo.md`](repository-setup/project-repo.md)** - General project setup

### **🤖 AI Integration**
- **[`ai-integration/ollama-setup.md`](ai-integration/ollama-setup.md)** - Local AI with Ollama
- **[`ai-integration/openai-setup.md`](ai-integration/openai-setup.md)** - OpenAI API integration
- **[`ai-integration/custom-prompts.md`](ai-integration/custom-prompts.md)** - Customizing AI prompts

### **⚙️ Automation Workflows** 
- **[`automation-workflows/github-actions.md`](automation-workflows/github-actions.md)** - CI/CD integration
- **[`automation-workflows/batch-processing.md`](automation-workflows/batch-processing.md)** - Processing multiple repos
- **[`automation-workflows/custom-validation.md`](automation-workflows/custom-validation.md)** - Custom validation rules

### **🔄 Migration Guides**
- **[`migration-guides/v1-to-v4.md`](migration-guides/v1-to-v4.md)** - Upgrading from older versions
- **[`migration-guides/cleanup-existing-repo.md`](migration-guides/cleanup-existing-repo.md)** - Adding CIP to existing projects

---

## 🎯 **Quick Start Scenarios**

### **"I want to add CIP to my Python package"**
```bash
# Quick setup with AI descriptions
cip init --type sdk --ai-provider ollama
cip ai-metadata --force
cip validate
```
👉 **Full guide**: [`repository-setup/sdk-repo.md`](repository-setup/sdk-repo.md)

### **"I need to process 50 repositories at once"**
```bash
# Batch processing with validation
./scripts/maintenance/validate-all.ps1 -WorkspacePath "C:\Projects"
./scripts/maintenance/update-metadata.sh /home/user/projects
```
👉 **Full guide**: [`automation-workflows/batch-processing.md`](automation-workflows/batch-processing.md)

### **"I want CI/CD to validate my CIP setup"**
```yaml
# Add to .github/workflows/cip.yml
- uses: ./scripts/github-actions/cip-validate
```
👉 **Full guide**: [`automation-workflows/github-actions.md`](automation-workflows/github-actions.md)

### **"I have an old CIP setup that needs updating"**
```bash
# Migration script
python scripts/migration/upgrade-to-v4.py --backup
cip validate --fix-issues
```
👉 **Full guide**: [`migration-guides/v1-to-v4.md`](migration-guides/v1-to-v4.md)

---

## 💡 **Real-World Use Cases**

### **Individual Developer Scenarios**

#### **Scenario 1: "My Utils Folder is a Mystery"**
**Problem:** You have a `utils/` directory with helpful functions, but you can't remember what's in there.

**Solution with CIP:**
```bash
cd my-project/
cip init --type project --title "My Web App"
cip ai-metadata --force
```

**Result:**
```yaml
# Before
utils/:
  description: "Utility functions"

# After (AI-generated)
utils/:
  description: "Authentication helpers, date formatting utilities, API response parsers, and custom React hooks for form validation"
```

#### **Scenario 2: "Research Repository Chaos"**
**Problem:** Your research repository has experiments everywhere with no organization.

**Solution with CIP:**
```bash
cip init --type theory --title "Quantum Field Research"
# Review generated structure
cip generate-instructions --validate
```

**Result:** Organized experiments/, theory/, and cognition/ directories with clear metadata.

### **Team & Organization Scenarios**

#### **Scenario 3: "New Team Members Are Lost"**
**Problem:** New team members can't understand your repository structure.

**Solution:** AI-generated instructions and validation questions help onboard new developers.

#### **Scenario 4: "Multi-Repository Workspace"**
**Problem:** Managing metadata across 20+ repositories.

**Solution:** Batch processing scripts maintain consistency across all projects.

---

## 🔗 **Related Documentation**

- **Getting started**: [`../user-guide/`](../user-guide/)
- **Scripts**: [`../scripts/`](../scripts/)
- **Architecture**: [`../architecture/`](../architecture/)
- **Case studies**: [`../case-studies/`](../case-studies/)
