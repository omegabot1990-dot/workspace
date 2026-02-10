# PROCESSES

This file defines the operating workflow for this OpenClaw instance.

## Purpose

- The Obsidian **vault** is the shared knowledge graph (“brain”) for research.
- The **workspace** repo stores operational process/config for the assistant.

## Vault structure (repo: `omegabot1990-dot/vault`)

- `001 - inbox/` — assistant-created items that require Batman’s attention.
- `002 - research/` — research zettels, MOCs, definitions, code notes.
- `008 - templates/` — templates (inbox, zettel, moc).
- `009 - help/` — vault usage help.

## Creating inbox items

When creating a new inbox item:

- Location: `vault/001 - inbox/`
- Template: `008 - templates/node - inbox.md`
- Must include:
  - `status: Backlog` (initial)
  - `description: ...` (required)
  - `task type`: capture | organise | distil | plan | execute
  - `urgency level`: urgent | not urgent
  - `importance level`: important | not important
  - `parent nodes`: link to a parent MOC/Zettel

## Creating zettels / MOCs

- Zettel: use `008 - templates/node - zettel.md`
- MOC: use `008 - templates/node - moc.md`
- Graph invariant: every new MOC/Zettel must link to a **parent** MOC or Zettel.

## Recursive learning workflow

- Start from a **paper**.
- Breadth-first pass (assistant):
  - Extract candidate concepts.
  - If a concept note does not exist yet in `002 - research/`, create it as a zettel and link it to an appropriate parent.
- Depth-first pass (Batman):
  - Deep study, expansion, derivations, refinements.

## Backups

- Workspace backup trigger: user says "backup the workspace" → commit + push workspace Markdown files.
- Vault auto-backup: daily cron at 02:00 Europe/Amsterdam.
