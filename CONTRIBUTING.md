# Contributing to NEXORA AI

## Overview
Nexora AI is an open standard and universal catalog of 3,000 AI agent skills. Contributions that expand, refine, or validate skills are welcome.

## Guidelines for Skill Creation
1. **Canonical Schema**: Every skill MUST adhere to `schemas/skill_schema.json`.
2. **Zero-Comment Rule**: Source code, configurations, and scripts MUST NOT contain any comment syntax.
3. **No Duplicate Capabilities**: Every skill must address a distinct engineering, architectural, or domain problem.
4. **Actionable Instructions**: Every skill must define explicit execution workflows, decision logic, safety restrictions, and validation criteria.
5. **Cross-Platform Compatibility**: Skills must define supported platforms and require only standard agent capabilities.

## Pull Request Process
1. Fork the repository and create a feature branch.
2. Validate new skills using the automated test suite:
   ```bash
   python -m unittest discover tests
   ```
3. Verify zero-comment policy enforcement:
   ```bash
   python scripts/verify_no_comments.py
   ```
4. Submit the pull request with a description of the domain improvements.

