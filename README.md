# OpenClaw Workspace

This repository contains the **OpenClaw agent workspace** for this instance.

## What’s in here

- `SOUL.md` — the assistant’s tone/persona and behavioral guidance.
- `USER.md` — user-specific preferences/context.
- `IDENTITY.md` — assistant identity metadata (name/vibe/avatar).
- `TOOLS.md` — environment/tooling notes (local setup specifics).
- `HEARTBEAT.md` — periodic check tasks (empty = no heartbeat tasks).
- `AGENTS.md` — workspace conventions and operating rules.
- `BOOTSTRAP.md` — first-run onboarding checklist (may be deleted after setup).
- `memory/` — daily durable memory notes (e.g. `memory/YYYY-MM-DD.md`).

## Notes

- Conversation/session transcripts are stored outside this repo under `~/.openclaw/agents/<agentId>/sessions/*.jsonl`.
- Be careful committing secrets. Prefer OAuth/device flows over pasting tokens/passwords.
