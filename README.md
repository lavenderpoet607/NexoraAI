# NEXORA AI

> **One Intelligence. 3,000+ Capabilities.**

Universal Multi-Platform AI Agent Skills, Subagents, and Workflow Ecosystem.

---

## Overview

**NEXORA AI** is an enterprise-grade ecosystem providing exactly **3,000 unique, practical, reusable, and independently useful AI agent skills** spanning 16 comprehensive domains. Built upon a single canonical specification, Nexora AI bridges the gap between agent platforms by providing high-performance native exports and adapters for all leading AI agent environments.

## Supported Platforms

Nexora AI provides first-class support and native adapters for:

- **Google Antigravity**
- **Claude Code & Claude Desktop**
- **Cursor** (`.cursorrules`, `.cursor/rules`)
- **Windsurf** (`.windsurfrules`)
- **GitHub Copilot** (`.github/copilot-instructions.md`)
- **Cline** (`.clinerules`)
- **Roo Code** (`.roomodes`)
- **Gemini CLI**
- **OpenAI Codex**
- **Continue** (`.continue/config.json`)
- **Aider** (`.aider.conf.yml`)

---

## 3,000 Skills Taxonomy

Nexora AI organizes 3,000 unique capabilities across 16 core engineering and creative disciplines:

| Domain | Category | Target Skills | Description |
|---|---|---|---|
| A | Software Engineering | 220 | Architecture, backend, frontend, API design, refactoring, code review |
| B | Programming Languages | 240 | Python, JS, TS, Go, Rust, Java, C++, Swift, Kotlin, PHP, C#, Dart, SQL |
| C | Web Development | 220 | React, Next.js, Vue, Angular, Laravel, Django, FastAPI, Node.js, Tailwind |
| D | Mobile Development | 160 | Flutter, Android, iOS, React Native, KMP, mobile UI/testing/performance |
| E | Game Development | 160 | Roblox Studio, Unity, Unreal Engine, Godot, game AI, physics, shaders |
| F | AI & Machine Learning | 240 | LLM engineering, multi-agent systems, RAG, vector DBs, fine-tuning |
| G | DevOps & Infrastructure | 200 | Docker, Kubernetes, CI/CD, Terraform, Linux, cloud ops, monitoring |
| H | Cybersecurity & Defense | 200 | Secure coding, auditing, threat modeling, malware defense, OWASP |
| I | Database Engineering | 180 | PostgreSQL, MySQL, MongoDB, Redis, Supabase, Firebase, query tuning |
| J | UI/UX & Design | 160 | Design systems, accessibility, typography, responsive layouts, Figma |
| K | Automation | 160 | Browser automation, RPA, workflow orchestration, cron scheduling |
| L | Documentation & Productivity | 140 | Technical writing, architecture decision records, API docs, planning |
| M | Data Engineering | 180 | ETL pipelines, Spark, BigQuery, data cleaning, streaming, analytics |
| N | Creative Production | 140 | 3D Blender modeling, animation, video production, procedural audio |
| O | Quality Engineering | 180 | Unit testing, integration testing, E2E automation, load testing |
| P | Cloud & Distributed Systems | 220 | Microservices resiliency, event-driven architecture, service mesh |
| **Total** | **16 Domains** | **3,000** | **Complete, distinct, non-duplicative agent capabilities** |

---

## Architectural Highlights

### 1. Canonical Schema Single Source of Truth
Every skill is defined strictly against `schemas/skill_schema.json` (JSON Schema draft-07) with 19 mandatory fields:
- `id`: Deterministic namespace identifier (`nexora-<cat>-<subcat>-<num>`)
- `name`: Unique, action-oriented name
- `purpose`: Precise functional objective
- `category` & `subcategory`: Hierarchical domain classification
- `description`: Detailed technical capability summary
- `supported_platforms`: Compatibility flags
- `activation_conditions`: Trigger phrases and file match patterns
- `required_inputs` & `expected_outputs`: Input/output contracts
- `execution_workflow`: Step-by-step procedure
- `decision_logic`: Heuristics and branching rules
- `tool_requirements` & `dependencies`: Tooling boundaries
- `safety_restrictions`: Defensive operational guards
- `validation_criteria`: Acceptance testing specifications
- `practical_examples`: Concrete usage scenarios
- `related_skills`: Graph connections within Nexora
- `version`: Semantic versioning

### 2. High-Performance SQLite FTS5 Index
Nexora embeds an indexed SQLite engine (`registry/nexora_registry.db`) featuring full-text search (FTS5) for sub-millisecond skill querying and retrieval without loading massive catalogs into memory.

### 3. Smart Cache and Token Management
- Content-addressable SHA-256 caching for file inputs and skill state.
- Progressive context loading: load only the required skill definition during task execution.
- Selective skill discovery avoiding context-window saturation.

### 4. Active Multi-Agent Orchestration
Nexora defines and leverages native subagents across 5 specialized roles:
- `nexora-architect`: System design and taxonomy integrity.
- `nexora-research`: Platform standards and adapter compliance.
- `nexora-swe`: Registry, search, caching, and batch pipelines.
- `nexora-testing`: Automated testing and schema validation.
- `nexora-security`: Defensive auditing and comment policy verification.

### 5. Strict Zero-Comment Policy
To maximize execution density, readability, and deterministic behavior, all generated source code and configuration files contain strictly **zero comments** (`#`, `//`, `/* */`, etc.).

---

## Quick Start

### Installation

```bash
git clone https://github.com/nexora-ai/nexora-ai.git
cd NexoraAI
pip install -e .
```

### Searching Skills

```bash
python -m nexora.cli search "rag vector database"
python -m nexora.cli info --id nexora-ai-rag-0001
```

### Exporting to Agent Platforms

```bash
# Export for Google Antigravity
python -m nexora.cli export --platform antigravity --output ./skills

# Export for Claude Code
python -m nexora.cli export --platform claude --output .claude/skills

# Export for Cursor
python -m nexora.cli export --platform cursor --output .cursorrules
```

---

## Project Structure

```
NexoraAI/
├── README.md                      # Overview and master catalog documentation
├── PLAN.md                        # Master execution plan
├── IMPLEMENTATION.md              # Technical implementation details
├── TEST_REPORT.md                 # Automated test and quality verification report
├── ARCHITECTURE.md                # System architecture blueprint
├── COMPATIBILITY.md               # Platform adapter and compatibility matrix
├── INSTALLATION.md                # Deployment and installation guide
├── CONTRIBUTING.md                # Contribution and skill authoring rules
├── CHANGELOG.md                   # Version history
├── SKILL_CATALOG.md               # Complete searchable index of all 3,000 skills
├── schemas/                       # Canonical JSON schemas
│   ├── skill_schema.json
│   └── platform_schema.json
├── categories/                    # Taxonomy definition and ID allocations
│   └── taxonomy_matrix.json
├── core/                          # Core runtime engine
│   ├── registry.py
│   ├── cache.py
│   ├── search.py
│   ├── router.py
│   ├── validator.py
│   └── exporter.py
├── nexora/                        # Unified CLI package
│   └── cli.py
├── scripts/                       # Pipelines and verification tooling
│   ├── batch_generator.py
│   ├── export_platforms.py
│   └── verify_no_comments.py
├── skills/                        # 3,000 Canonical skill definitions
├── platforms/                     # Platform adapter templates
├── registry/                      # SQLite FTS5 database and JSON indexes
├── checkpoints/                   # Execution checkpoints
└── tests/                         # Automated test suite
```

---

## License

Nexora AI is released under the MIT License.

