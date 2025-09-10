# 🧠 CIP-Core: Cognition Index Protocol Implementation

**AI-Enhanced Repository Automation for Scientific Computing**

[![Version](https://img.shields.io/badge/version-0.1.0--dev-blue)](https://github.com/dawnfield-institute/cip-core)
[![Python](https://img.shields.io/badge/python-3.8+-green)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Status](https://img.shields.io/badge/status-active%20development-orange)](https://github.com/dawnfield-institute/cip-core)

---

## 🎯 Overview

CIP-Core is the foundational implementation of the **Cognition Index Protocol (CIP)**, providing AI-enhanced automation for repository management, validation, and cross-ecosystem navigation. Originally designed for the Dawn Field Theory ecosystem, CIP-Core enables reproducible scientific computing through intelligent metadata generation and protocol-driven validation.

### ✨ Key Features

- **🤖 AI-Enhanced Metadata**: Intelligent directory descriptions using local Ollama integration
- **� Comprehensive Validation**: Schema compliance, quality checks, and ecosystem link validation
- **📊 Quality Assurance**: Automated detection of generic content and meaningful description requirements
- **🗺️ Cross-Repository Navigation**: Seamless linking and discovery with `repo://` URL scheme
- **🛠️ Developer CLI**: Complete command-line toolkit for repository automation
- **📋 AI Instruction Generation**: Automated guidance files for AI agents and repository understanding
- **� Ecosystem Integration**: Multi-repository workflows and dependency management

## 🚀 Quick Start

### Installation

```bash
# Install from source (development)
git clone https://github.com/dawnfield-institute/cip-core.git
cd cip-core
pip install -e .

# Verify installation
cip --version
```

### Basic Usage

```bash
# Initialize CIP metadata in your repository
cip init --type protocol --title "My Project"

# Generate AI-enhanced metadata for all directories
cip ai-metadata --force --model codellama:latest

# Generate AI instruction files
cip generate-instructions --validate

# Validate repository compliance
cip validate

# Bootstrap complete CIP automation
cip bootstrap --type sdk
```

### AI Enhancement Workflow

```bash
# Test AI integration
cip ai-enhance --test-only

# Generate meaningful metadata (replaces generic descriptions)
cip ai-metadata --force --path ./my-repository

# Create navigation instructions for AI agents
cip generate-instructions --validate

# Validate quality and compliance
cip validate --format json
```

## 📚 Documentation

### 📖 Getting Started
- **[Quick Start Guide](docs/README.md)** - Overview of documentation structure
- **[Technical Documentation](docs/technical/README.md)** - Implementation details and API reference
- **[Integration Guide](docs/technical/README.md#integration-guide)** - Add CIP to existing projects

### 🏛️ Architecture & Design
- **[Architecture Documentation](docs/architecture/)** - Protocol specifications and design
- **[GPT Integration](docs/gpt/)** - AI integration patterns and prompts
- **[Case Studies](docs/case_studies/)** - Real-world implementation examples

### 🚦 Planning & Roadmap
- **[Development Roadmap](roadmap/README.md)** - Planned features and timeline
- **[TODO List](todo/README.md)** - Current development priorities
- **[Known Limitations](docs/limitations/README.md)** - Current constraints and workarounds

## 🏗️ Project Structure

```
cip-core/
├── cip_core/              # 🐍 Core Python package
│   ├── schemas/           #    📋 YAML schema validation
│   ├── validators/        #    ✅ Compliance checking
│   ├── automation/        #    🤖 AI-enhanced metadata generation
│   ├── navigation/        #    🗺️ Cross-repository linking
│   ├── instructions/      #    📖 AI instruction generation
│   ├── ollama_local/      #    🤖 Local AI integration
│   ├── vm/               #    ☁️ Cloud VM service integration
│   ├── cli/              #    🛠️ Command-line interface
│   └── utils/            #    🔧 Common utilities
├── docs/                 # 📚 Comprehensive documentation
│   ├── architecture/     #    🏛️ Protocol specifications
│   ├── technical/        #    🔧 Implementation guides
│   ├── case_studies/     #    📝 Real-world examples
│   ├── gpt/             #    🤖 AI integration guides
│   └── limitations/      #    ⚠️ Known constraints
├── roadmap/             # 🗺️ Development planning
├── todo/                # 📋 Current priorities
├── templates/           # 📄 Configuration templates
└── tests/              # 🧪 Test suite
```

## 🛠️ CLI Commands

### Core Operations
```bash
cip init                    # Initialize repository with CIP metadata
cip validate               # Check repository compliance
cip bootstrap              # Complete CIP setup automation
```

### AI-Enhanced Features
```bash
cip ai-metadata           # Generate intelligent descriptions
cip ai-enhance            # Full AI enhancement workflow
cip generate-instructions # Create AI guidance files
```

### Repository Navigation
```bash
cip resolve               # Resolve repo:// URLs to content
cip list-repos           # List ecosystem repositories
cip validate-links       # Check cross-repository links
```

### Development Tools
```bash
cip generate-metadata    # Rule-based metadata generation
cip vm trigger           # Cloud AI analysis (planned)
cip vm status           # Check analysis job status
```
├── tools/             # Standalone utilities
└── tests/             # Comprehensive test suite
```

## 🤝 Contributing

This repository is currently in private development. Once stabilized, we'll welcome community contributions following the Dawn Field Theory governance model.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

**Why MIT?** CIP-Core is designed as infrastructure for the broader scientific computing ecosystem. The MIT license ensures maximum compatibility and adoption across academic, commercial, and open source projects.

---

**Part of the [Dawn Field Theory](https://github.com/dawnfield-institute/dawn-field-theory) ecosystem**
