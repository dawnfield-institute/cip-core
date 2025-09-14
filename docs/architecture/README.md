# 🏛️ Architecture

> **Technical design and system architecture of CIP-Core**

This section contains the foundational design documents that explain how CIP works internally, the reasoning behind key decisions, and the evolution of the system.

---

## 📖 **Documentation in this section:**

### **Current Architecture (v4)**
- **[`README.md`](README.md)** - Architecture overview
- **[`core-design.md`](core-design.md)** - **Primary design document** (consolidates v1-v3)
- **[`data-flow.md`](data-flow.md)** - How data moves through the system
- **[`plugin-system.md`](plugin-system.md)** - Extensibility architecture
- **[`ai-integration.md`](ai-integration.md)** - AI provider integration patterns

### **Historical Documents**
- **[`legacy/`](legacy/)** - Previous architecture versions (v1-v3)

---

## 🔄 **Architecture Evolution**

### **Version 4 (Current) - Unified Architecture**
- **Status**: 🚧 In development
- **Focus**: Consolidation and cleanup
- **Key Features**: Single CIPEngine, unified metadata system, plugin architecture

### **Previous Versions**
- **v3**: Metadata architecture focus → [`legacy/v3-metadata.md`](legacy/v3-metadata.md)
- **v2**: GPT integration → [`legacy/v2-gpt-architecture.md`](legacy/v2-gpt-architecture.md)  
- **v1**: Original CIP protocol → [`legacy/v1-architecture.md`](legacy/v1-architecture.md)

---

## 🎯 **Key Architectural Principles**

### **1. Single Responsibility**
Each class has one clear purpose and well-defined boundaries.

### **2. Composition over Inheritance**
Use dependency injection and composition for shared functionality.

### **3. Plugin Architecture**
Extensible validation and generation systems for custom needs.

### **4. Clear Data Flow**
Explicit input/output contracts and predictable state management.

---

## 🔗 **For Developers**

- **Implementation details**: See [`../developer-guide/class-hierarchy.md`](../developer-guide/class-hierarchy.md)
- **API reference**: See [`../developer-guide/api-reference.md`](../developer-guide/api-reference.md)
- **Contributing**: See [`../developer-guide/contributing.md`](../developer-guide/contributing.md)
