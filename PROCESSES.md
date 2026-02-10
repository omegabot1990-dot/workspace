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
- Set `bot: true` if created by the assistant

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

Note: Batman applies highlights during study; assistant should not add highlights to newly created zettels unless explicitly asked.

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
  - Set `bot: true` if created by the assistant
  - Timestamped zettels are used for: `paper | note | code | math`
  - `paper` = summary of a paper
  - `note` = leaf/atomic concept node (e.g. objective function) with a parent (zettel or MOC) and linked content to other zettels
  - `code` / `math` = paradigms as specified below

### Zettel workflows (robust spec)

### Creation commands (draft standard)

- `note <parent> <topic name>`
- `math <parent> <topic name>`
- `paper <parent> <alphaXiv link>`

Interpretation:
- `note`: non-math conceptual zettel
- `math`: math concept zettel (use math-only framing)
- `paper`: paper zettel sourced from alphaXiv blog

#### Global zettel rules (all kinds)

- Filename timestamp: Europe/Amsterdam local time (DST-aware), `YYYYMMDDHHMM - <topic>.md`
  - One-liner: `python3 -c "from datetime import datetime; from zoneinfo import ZoneInfo; print(datetime.now(ZoneInfo('Europe/Amsterdam')).strftime('%Y%m%d%H%M'))"`
- `title` in frontmatter: lowercase
- `aliases`: appropriate casing (e.g. Title Case)
- Writing style: bullet lists, concise, no trailing full stops
- Avoid meta-commentary like “in this vault” inside zettel content
- Do not add highlights or citations
- Use Obsidian LaTeX for math: inline `$...$`, display `$$...$$`
- Add a `[!MATH]` callout only when there is actual math (definition/formula)
  - Callout should be fully defined (Mean-style): short title, one-line explanation, then LaTeX in `$$...$$`

#### Note zettels

- Use when the topic is not primarily mathematical
- Research step: web search topic and verify against trusted sources (see list below)
- Output: very concise summary in simple words, but correct technical jargon

#### Math zettels

- Use when the topic is mathematical (keep it purely mathematical; avoid ML/application framing)
- Research step: web search topic and verify against trusted sources (see list below)
- Output: very concise summary in simple words, but correct technical jargon

#### Paper zettels (from alphaXiv blog)

- Topic naming:
  - `title`: paper name in lowercase
  - Replace `:` with `-`
  - `aliases`: exactly the alphaXiv blog header text (verbatim casing)
- alphaXiv link: Batman provides the alphaXiv URL
- Source: use alphaXiv blog as the primary source of sections/content and re-verify against the blog/paper content
- Required sections in this order:
  - `## Topics (not in KG yet)` (top of note)
  - `## Summary`
  - `## Problem`
  - `## Method`
  - `## Result`
  - `## Take Away`
  - `## Limitations`
  - `## Future Work`
- Missing topics handling:
  - Determine whether a topic is in KG by comparing against existing zettel topic names using normalization (casefold + strip + collapse whitespace + normalize `:`→`-`)
  - If unsure, include it in the missing-topics list
  - If a topic is not present in KG, list it under `## Topics (not in KG yet)` as `- [ ] <topic>`
  - Do not create new zettels for those topics
- Figures/graphs:
  - Embed relevant alphaXiv figures/graphs in Obsidian embed style `![](<url>)` similar to the InstructGPT example

#### MOC update rule

- After creating any zettel, update the parent MOC you provided:
  - If the topic entry exists under the relevant section, convert it to a checked link: `- [x] [[<zettel>|<Alias>]]`
  - If it is missing, add it under the correct section (`Topics` for concepts, `Papers` for papers) and mark it done

#### Trusted sources (default)

- StatQuest
- 3Blue1Brown
- Stanford notes
- Textbooks
- arXiv survey papers
- Emergent Mind
- D2L
- MOC: use `008 - templates/node - moc.md`
  - Batman owns/creates MOCs (assistant should not create MOCs)
  - MOC sections (always in this order): `## Topics`, `## Blogs`, `## Papers`, `## Videos`, `## Code`
    - Topics: checklist of concepts (typically no external links)
    - Blogs: external links to blogs/newsletters/resources
    - Papers: external links to paper platforms (alphaXiv/arXiv/OpenReview/etc), not random resources
    - Videos: external links to videos (YouTube, etc)
    - Code: external links to GitHub repos (GitHub links are Code)
    - Note: tools/services like Weights & Biases (wandb) and VastAI are treated as Blogs (resources), not Code
  - When restructuring MOCs, keep sub-items attached to their parent top-level item; only bin top-level items
  - When a zettel exists for a concept, ensure the MOC has a checked link entry: `- [x] [[<zettel>|<Concept>]]`
  - If a concept is missing from the MOC, add it and check it once the zettel is created
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
