# NEXORA AI: Installation and Deployment Guide

## Prerequisites
- Python 3.10+ (Tested on Python 3.14.5)
- Node.js 18+ (Optional, for web/JS adapters)
- Git 2.30+

## Local Installation
Clone the repository and install Nexora AI:

```bash
git clone https://github.com/nexora-ai/nexora-ai.git
cd NexoraAI
pip install -e .
```

## Initializing the Ecosystem
Initialize the registry and build the local SQLite search index:

```bash
python -m nexora.cli init
```

## Searching Skills
Search for skills across 3,000 capabilities:

```bash
python -m nexora.cli search "jwt authentication"
python -m nexora.cli search "kubernetes ingress"
python -m nexora.cli info --id nexora-swe-be-0001
```

## Exporting for Specific Platforms
Export skills or skill packs for your target AI agent environment:

### Google Antigravity
```bash
python -m nexora.cli export --platform antigravity --output .gemini/antigravity/skills
```

### Claude Code
```bash
python -m nexora.cli export --platform claude --output .claude/skills
```

### Cursor
```bash
python -m nexora.cli export --platform cursor --output .cursorrules
```

### Windsurf
```bash
python -m nexora.cli export --platform windsurf --output .windsurfrules
```

### GitHub Copilot
```bash
python -m nexora.cli export --platform copilot --output .github/copilot-instructions.md
```

### Cline
```bash
python -m nexora.cli export --platform cline --output .clinerules
```

### Roo Code
```bash
python -m nexora.cli export --platform roo --output .roomodes
```

## Running Automated Validation
Execute the complete quality verification suite:

```bash
pytest tests/
```

