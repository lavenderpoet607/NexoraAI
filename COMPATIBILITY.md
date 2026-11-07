# NEXORA AI COMPATIBILITY MATRIX AND ADAPTER SPECIFICATION

This document details the exact technical specifications, configuration formats, activation triggers, capability constraints, and adapter compilation designs across all eleven supported AI developer platforms.

---

## 1. Executive Platform Comparison Matrix

| Platform | Primary File Path | Format Type | Context Window | Rec. Instruction Budget | MCP Support | Subagent Support | Background Tasks | Reactive Wakeup | Terminal Execution | Git Automation | Mode Switching |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Google Antigravity | `.gemini/antigravity/` | Native Orchestration | 2,000,000 | 65,536 | Native (Eager/Lazy) | Yes (Multi-agent) | Yes (`run_command`, daemon) | Yes (Message delivery) | Yes (PowerShell/Bash) | Yes | Yes |
| Claude Code | `CLAUDE.md` | Markdown Rules | 200,000 | 2,500 | Yes (stdio JSON-RPC) | Yes (Forked subagents) | No | No | Yes (Direct shell) | Yes | No |
| Cursor | `.cursor/rules/{rule_name}.mdc` | Markdown + Frontmatter | 200,000 | 4,000 | Yes (Cursor MCP) | No | No | No | Yes (Integrated terminal)| No | No |
| Windsurf | `.windsurfrules` | Markdown Rules | 200,000 | 3,500 | Yes (Cascade MCP) | No | No | No | Yes (Cascade actions) | No | Yes |
| GitHub Copilot | `.github/copilot-instructions.md` | Plain Markdown | 128,000 | 2,000 | No | No | No | No | Yes (Interactive terminal)| No | No |
| Cline | `.clinerules` | Plain Markdown | 200,000 | 4,500 | Yes (Dynamic MCP) | No | No | No | Yes (Shell approval loop)| Yes | Yes |
| Roo Code | `.roomodes` | JSON Mode Config | 200,000 | 5,000 | Yes (Per-mode MCP) | No | No | No | Yes (Group-based) | Yes | Yes |
| Gemini CLI | `GEMINI.md` | Markdown Context | 2,000,000 | 32,768 | Yes (Function Calling) | No | No | No | No | No | No |
| OpenAI Codex | `codex_prompt.md` | Assistant Manifest | 128,000 | 8,000 | No (Function calling) | No | No | No | No (Sandbox only) | No | No |
| Continue | `.continue/config.json` | JSON + Rules Dir | 200,000 | 4,000 | Yes (Continue MCP) | No | No | No | Yes (Context commands) | No | No |
| Aider | `.aider.conf.yml` | YAML + CONVENTIONS.md | 200,000 | 3,000 | No | Yes (Architect/Editor) | No | No | Yes (Slash `/run`) | Yes | Yes |

---

## 2. Platform Deep Dives

### 2.1 Google Antigravity

- Vendor: Google DeepMind
- Primary Configuration Files:
  - Agent Manifest: `agents/{agent_name}.json`
  - Workspace Context: `.gemini/antigravity/`
  - Artifact Storage: `<appDataDir>/brain/<conversation_id>/`
  - Scratch Environment: `<appDataDir>/brain/<conversation_id>/scratch/`
  - Tool Schemas: `<appDataDir>/mcp/{server_name}/{tool_name}.json`
- Native Configuration Syntax:
  - Agent instructions injected as system prompt
  - Structured artifacts formatted in GitHub Flavored Markdown with metadata headers
  - MCP tool definitions stored as individual JSON schema definitions
- Activation Triggers:
  - Direct user conversational prompts
  - High-priority reactive message events from subagents or background tasks via `send_message`
  - One-shot countdown timers and cron schedules configured through `schedule`
  - Process termination signals monitored through `manage_task`
- Capability Limits:
  - Maximum context window: 2,000,000 tokens
  - Maximum recommended instruction budget: 65,536 tokens
  - Subagent recursion depth: Arbitrary hierarchical subagent trees
  - File read buffer: 800 lines or 46,080 bytes per invocation
- Tool Execution Mechanics:
  - Eager MCP tools registered directly as native tools
  - Lazy MCP tools invoked dynamically through `call_mcp_tool`
  - Asynchronous background commands executed via `run_command` with `WaitMsBeforeAsync`
- Nexora Adapter Design:
  - Generates specialized subagent manifests in `agents/`
  - Formats instructions with proactive delegation patterns and explicit tool usage protocols
  - Produces clean JSON schemas for lazy-loaded tools in `schemas/`

### 2.2 Claude Code

- Vendor: Anthropic
- Primary Configuration Files:
  - Workspace Instructions: `CLAUDE.md`
  - Local Project Settings: `.claude.json`
  - Global Configuration: `~/.claude.json`
  - Persistent Memory: `.claude/memory/`
- Native Configuration Syntax:
  - Single markdown file containing concise architecture guidelines, build scripts, test commands, and coding conventions
  - Supports hierarchical overrides where subdirectories contain nested `CLAUDE.md` files
- Activation Triggers:
  - CLI execution via `claude` or `claude "<prompt>"`
  - Built-in slash commands: `/help`, `/compact`, `/cost`, `/doctor`, `/init`, `/review`, `/clear`
  - Terminal tool loop triggers based on file diffs or test failures
- Capability Limits:
  - Maximum context window: 200,000 tokens
  - Maximum recommended instruction budget: 2,500 tokens
  - Tool output limit: 30,000 characters per execution step
- Tool Execution Mechanics:
  - Direct local bash command execution
  - Native file manipulation primitives: `View`, `Edit`, `Replace`, `GlobTool`, `GrepTool`
  - Stdio-based MCP server integration
- Nexora Adapter Design:
  - Compiles universal skill catalog into a dense, high-signal `CLAUDE.md`
  - Groups instructions into sections: Architecture, Command Cheat Sheet, Code Style, and Safety Invariants
  - Enforces zero-comment policy across all emitted code examples

### 2.3 Cursor

- Vendor: Anysphere
- Primary Configuration Files:
  - Modular Rules: `.cursor/rules/{rule_name}.mdc`
  - Root Legacy Rules: `.cursorrules`
  - MCP Client Configuration: `.cursor/mcp.json`
- Native Configuration Syntax:
  - MDC format featuring YAML frontmatter metadata combined with markdown instructions:
    - `description`: Human-readable summary of the rule
    - `globs`: File match patterns defining activation scope
    - `alwaysApply`: Boolean flag determining whether the rule is loaded globally
- Activation Triggers:
  - File match glob activation when target source files are opened or edited
  - Always-apply rules loaded unconditionally into every session
  - Interactive at-mentions: `@Files`, `@Folders`, `@Code`, `@Docs`, `@Git`
  - Composer agent execution (Cmd+I / Ctrl+I)
  - Inline code editor edits (Cmd+K / Ctrl+K)
- Capability Limits:
  - Maximum context window: 200,000 tokens
  - Maximum recommended instruction budget: 4,000 tokens across all active rules
  - Codebase embedding search over project git tree
- Tool Execution Mechanics:
  - Integrated terminal execution with user review
  - Multi-file patch application via Composer
  - MCP servers configured via JSON definitions
- Nexora Adapter Design:
  - Splits universal skills into modular `.cursor/rules/{rule_name}.mdc` files organized by domain
  - Generates `.cursorrules` fallback for backward compatibility
  - Automatically maps skill triggers to specific file globs

### 2.4 Windsurf

- Vendor: Codeium
- Primary Configuration Files:
  - Workspace Rules: `.windsurfrules`
  - Hierarchical Rules: `.windsurf/rules/`
  - MCP Client Settings: `~/.codeium/windsurf/mcp_config.json`
- Native Configuration Syntax:
  - Plain markdown document structured into distinct functional sections
  - Directive-based guidance instructing the Cascade engine on code generation, testing, and file navigation
- Activation Triggers:
  - Cascade conversational chat panel
  - Write mode autonomous edits
  - Real-time Supercomplete suggestions
  - File focus changes triggering workspace context indexing
- Capability Limits:
  - Maximum context window: 200,000 tokens
  - Maximum recommended instruction budget: 3,500 tokens
- Tool Execution Mechanics:
  - Cascade Flow tools: multi-file modifications, command runs, code search
  - Windsurf MCP server hooks
- Nexora Adapter Design:
  - Compiles skills into a structured `.windsurfrules` document
  - Segregates directives into Core Protocols, Architecture Boundaries, and Quality Assurance Gates

### 2.5 GitHub Copilot

- Vendor: GitHub / Microsoft
- Primary Configuration Files:
  - Workspace Prompt: `.github/copilot-instructions.md`
  - VS Code Settings: `.vscode/settings.json` (`github.copilot.chat.codeGeneration.instructions`)
- Native Configuration Syntax:
  - Markdown document detailing coding guidelines, style preferences, and disallowed patterns
  - Injected automatically into the context of GitHub Copilot Chat
- Activation Triggers:
  - Copilot Chat queries targeting `@workspace`, `@terminal`, or `@vscode`
  - Slash commands: `/explain`, `/fix`, `/tests`, `/doc`, `/setupTests`
  - Ghost text inline completions
- Capability Limits:
  - Maximum context window: 128,000 tokens
  - Maximum recommended instruction budget: 2,000 tokens
- Tool Execution Mechanics:
  - Code generation suggestions in editor buffers
  - Suggested terminal commands requiring explicit user execution
  - No autonomous subagent loops or external MCP server connectivity
- Nexora Adapter Design:
  - Generates highly condensed instructions focusing strictly on code standards, framework conventions, and forbidden syntax
  - Truncates verbose operational workflows to fit Copilot prompt limits

### 2.6 Cline

- Vendor: Cline
- Primary Configuration Files:
  - Workspace Rules: `.clinerules`
  - MCP Server Registry: `cline_mcp_settings.json`
  - Workflows Directory: `.cline/`
- Native Configuration Syntax:
  - Markdown file appended to system prompt
  - Strict step-by-step problem-solving instructions
- Activation Triggers:
  - Task goal initiation by user
  - Transition between Plan Mode and Act Mode
  - Tool execution confirmation events
- Capability Limits:
  - Maximum context window: 200,000 tokens
  - Maximum recommended instruction budget: 4,500 tokens
- Tool Execution Mechanics:
  - Autonomous tool execution loop: `execute_command`, `read_file`, `write_to_file`, `replace_in_file`, `browser_action`, `use_mcp_tool`
  - User authorization checkpoint before modifying filesystem or running shell commands
- Nexora Adapter Design:
  - Formats instructions to enforce systematic exploration before editing
  - Enforces atomic file diffs and mandatory test execution steps

### 2.7 Roo Code

- Vendor: Roo Code
- Primary Configuration Files:
  - Custom Modes Manifest: `.roomodes`
  - Global Workspace Rules: `.roorules` or `.clinerules`
- Native Configuration Syntax:
  - JSON configuration defining specialized operational roles:
    - `slug`: Unique mode identifier
    - `name`: Display label
    - `roleDefinition`: Role description and scope
    - `customInstructions`: Specialized prompt for the mode
    - `groups`: Allowed tool capabilities (`read`, `edit`, `browser`, `command`, `mcp`)
- Activation Triggers:
  - Mode selection switch in user interface
  - Plan Mode and Act Mode transitions
  - Task submission under active mode
- Capability Limits:
  - Maximum context window: 200,000 tokens
  - Maximum recommended instruction budget: 5,000 tokens
- Tool Execution Mechanics:
  - Role-gated tool execution
  - Dynamic MCP tool routing
- Nexora Adapter Design:
  - Compiles universal skill clusters into dedicated Roo Code modes
  - Creates distinct modes: `nexora-architect` (read-only), `nexora-engineer` (full permissions), `nexora-auditor` (read and test only)

### 2.8 Gemini CLI

- Vendor: Google Cloud
- Primary Configuration Files:
  - Workspace Instructions: `GEMINI.md`
  - Runtime Settings: `.gemini/config.json`
- Native Configuration Syntax:
  - Markdown documentation containing system prompt directives, contextual references, and project conventions
  - JSON configuration specifying default model, temperature, safety filters, and function calling endpoints
- Activation Triggers:
  - Direct CLI commands: `gemini run`, `gemini chat`, `gemini query`
  - Stdin pipelines: `cat input | gemini`
  - Automated function calling responses
- Capability Limits:
  - Maximum context window: 2,000,000 tokens
  - Maximum recommended instruction budget: 32,768 tokens
- Tool Execution Mechanics:
  - Native Google Search grounding
  - Python execution sandbox
  - OpenAPI-based function calling schemas
- Nexora Adapter Design:
  - Compiles full skill manifests without aggressive compression, utilizing the large context window
  - Emits `GEMINI.md` alongside structured `.gemini/config.json`

### 2.9 OpenAI Codex

- Vendor: OpenAI
- Primary Configuration Files:
  - System Instructions: `codex_prompt.md`
  - Assistant Configuration: `.openai/assistant.json`
- Native Configuration Syntax:
  - Plain text or markdown prompt for system instructions
  - Assistant manifest JSON defining model identifier, tools array (`code_interpreter`, `file_search`, `function`), and parameter schemas
- Activation Triggers:
  - Assistant thread runs
  - Function calling response roundtrips
  - Batch evaluation scripts
- Capability Limits:
  - Maximum context window: 128,000 tokens
  - Maximum recommended instruction budget: 8,000 tokens
- Tool Execution Mechanics:
  - Isolated Python Code Interpreter sandbox
  - Vector store file search retrieval
  - Parallel function calling execution
- Nexora Adapter Design:
  - Converts universal skill actions into OpenAI Function Calling JSON schemas
  - Compiles core behavior into `codex_prompt.md` and generates `.openai/assistant.json`

### 2.10 Continue

- Vendor: Continue.dev
- Primary Configuration Files:
  - Assistant Configuration: `.continue/config.json`
  - Modular Rules Directory: `.continue/rules/{rule_name}.md`
  - Global Configuration: `~/.continue/config.json`
- Native Configuration Syntax:
  - JSON configuration declaring models, slash commands, context providers, and custom system messages
  - Modular markdown files in rules directory containing domain-specific guidelines
- Activation Triggers:
  - Chat panel invocations (Cmd+L / Ctrl+L)
  - Inline code edit requests (Cmd+I / Ctrl+I)
  - Custom slash commands: `/edit`, `/comment`, `/test`, `/share`, `/cmd`
  - Context provider mentions: `@file`, `@folder`, `@code`, `@diff`, `@terminal`
- Capability Limits:
  - Maximum context window: 200,000 tokens
  - Maximum recommended instruction budget: 4,000 tokens
- Tool Execution Mechanics:
  - Context providers extracting live editor and git metadata
  - Continue MCP client integrations
  - Suggested bash command generation
- Nexora Adapter Design:
  - Injects universal guidelines into `.continue/rules/nexora.md`
  - Updates `.continue/config.json` with Nexora slash commands and custom context providers

### 2.11 Aider

- Vendor: Paul Gauthier
- Primary Configuration Files:
  - Runtime Configuration: `.aider.conf.yml`
  - Project Conventions: `CONVENTIONS.md`
  - Model Settings: `.aider.model.metadata.json`
- Native Configuration Syntax:
  - YAML configuration defining execution flags, test commands, lint commands, and read-file arrays
  - Markdown conventions document read automatically at session startup
- Activation Triggers:
  - Terminal session launch via `aider`
  - Interactive slash commands: `/add`, `/drop`, `/run`, `/test`, `/lint`, `/architect`, `/commit`, `/undo`
  - Automatic git commit triggers after file modifications
- Capability Limits:
  - Maximum context window: 200,000 tokens
  - Maximum recommended instruction budget: 3,000 tokens
  - Repository map: 1,024 to 4,096 tokens allocated to AST symbol tree
- Tool Execution Mechanics:
  - Direct git repository tracking and automated commit authoring
  - Automated test and lint runner integration
  - Dual-model Architect and Editor collaboration mode
- Nexora Adapter Design:
  - Emits `.aider.conf.yml` referencing `CONVENTIONS.md`
  - Structures `CONVENTIONS.md` with explicit test-first requirements, commit conventions, and architectural invariants

---

## 3. Universal Nexora Adapter Architecture

### 3.1 Intermediate Representation Pipeline

Nexora AI maintains a single source of truth for all skills, subagents, and governance policies. The universal intermediate representation is compiled into platform-native configurations through a multi-stage compilation pipeline:

```
[Universal Skill Registry]
          |
          v
[Validation Engine] (schema validation, zero-comment verification)
          |
          v
[Platform Filter] (evaluates target platform capability flags)
          |
          +===> Google Antigravity Adapter ===> agents/{agent}.json + mcp/{tool}.json
          +===> Claude Code Adapter        ===> CLAUDE.md
          +===> Cursor Adapter             ===> .cursor/rules/{rule}.mdc
          +===> Windsurf Adapter           ===> .windsurfrules
          +===> GitHub Copilot Adapter     ===> .github/copilot-instructions.md
          +===> Cline Adapter              ===> .clinerules
          +===> Roo Code Adapter           ===> .roomodes
          +===> Gemini CLI Adapter         ===> GEMINI.md + .gemini/config.json
          +===> OpenAI Codex Adapter       ===> codex_prompt.md + .openai/assistant.json
          +===> Continue Adapter           ===> .continue/config.json + .continue/rules/
          +===> Aider Adapter              ===> .aider.conf.yml + CONVENTIONS.md
```

### 3.2 Feature Degradation & Fallback Strategy

When a skill requires capabilities not supported by a target platform, the adapter applies standardized fallback strategies:

1. Subagent Orchestration:
   - Antigravity: Native subagent processes with reactive wakeups.
   - Claude Code and Aider: Architect mode pairing.
   - Roo Code: Dedicated operational mode switching via `.roomodes`.
   - Single-Agent Platforms (Cursor, Windsurf, Copilot, Cline): In-prompt role decomposition and structured multi-phase execution plans.

2. MCP Integration:
   - Supported Platforms (Antigravity, Cursor, Windsurf, Cline, Roo Code, Continue): Native tool schemas and dynamic invocation.
   - Unsupported Platforms (Copilot, Aider, Codex): Generation of command-line recipes, shell scripts, or standard REST API wrappers.

3. Background Tasks and Scheduling:
   - Antigravity: Native daemon jobs and cron triggers via `schedule`.
   - Other Platforms: Generation of platform-external scheduling scripts or instructions for local operating system task runners.

### 3.3 Strict Comment Ban Enforcement

All Nexora adapters enforce an absolute zero-comment policy across all generated artifacts, code files, and configurations:
- Zero single-line comments in slash, hash, or dash syntax
- Zero multi-line block comments in slash-star, xml, or html syntax
- Zero docstrings or commented-out code segments
- Markdown files must use structural headings and list items without html comment annotations

---

## 4. Verification and Validation Guidelines

Before deploying configuration files to any target platform, the validation engine executes three mandatory checks:

1. Syntax Validation:
   - JSON configurations must parse strictly with standard JSON parsers.
   - YAML files must validate against the target schema without syntax deviations.
   - Frontmatter blocks in MDC files must contain required fields: `description`, `globs`, `alwaysApply`.

2. Token Budget Compliance:
   - Total instruction length must remain within recommended limits for the target platform to prevent prompt dilution.

3. Zero-Comment Verification:
   - Automated regular expression scanning across all output files to confirm zero comment tokens exist.
