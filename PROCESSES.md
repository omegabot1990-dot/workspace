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

## Highlighting / priority markers

Use Obsidian HTML `<mark style="background: ...;">...</mark>` highlights (not `==...==`).

Priority / urgency color scheme:
- High + Urgent: `<mark style="background: #FF5582A6;">Deep Work / Peak Flow</mark>`
- High + Not urgent: `<mark style="background: #ADCCFFA6;">Strategic Planning</mark>`
- Medium + Urgent: `<mark style="background: #FFB86CA6;">AI Co-Pilot / Sprint</mark>`
- Medium + Not urgent: `<mark style="background: #D2B3FFA6;">Curate & Stack</mark>`
- Low + Urgent: `<mark style="background: #BBFABBA6;">AI Auto-Pilot / Time-Box</mark>`
- Low + Not urgent: plain text `Archive / Backlog`.

When adding a highlighted item, include a short action label in-angle-brackets next to it, e.g. `<important>`, `<do later>`, `<quick read>`, `<skim>`, `<watch>`, based on context.

## Creating zettels / MOCs

- Zettel: use `008 - templates/node - zettel.md`
  - Timestamped zettels are used for: `paper | note | code | math`.
  - `paper` = summary of a paper.
  - `note` = leaf/atomic concept node (e.g. objective function) with a parent (zettel or MOC) and linked content to other zettels.
  - `code` / `math` = zettels with their own paradigms (Batman will specify).
- MOC: use `008 - templates/node - moc.md`
  - High-level concept map that mainly links to zettels; minimal/no content.
- Graph invariant: every new MOC/Zettel must link to a **parent** MOC or Zettel.
- Root parent: `[[research.base]]` is the root parent for the research graph.

## Recursive learning workflow

- Start from a **paper**.
- Breadth-first pass (assistant):
  1) Create **one zettel per paper**.
  2) Create an **MOC for the concepts in the paper**.
  3) BFS concept capture: if a concept note does not exist yet in `002 - research/`, create it as a zettel and link it to an appropriate parent.
- Depth-first pass (Batman):
  - Deep study, expansion, derivations, refinements.

## Backups

- Workspace backup trigger: user says "backup the workspace" → commit + push workspace Markdown files.
- Vault auto-backup: daily cron at 02:00 Europe/Amsterdam.
