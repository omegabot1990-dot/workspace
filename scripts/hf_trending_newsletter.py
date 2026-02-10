#!/usr/bin/env python3
"""Build daily newsletter from https://huggingface.co/papers/trending

This script lives in the WORKSPACE repo (operational code) and writes outputs into the
VAULT repo (notes).

Outputs (in vault):
- Creates/updates a daily note under `000 - daily notes/` with
  - Latest papers (filtered)
  - TLDR top papers (per-paper TLDR referencing which paper)
- Prints a Discord-ready TLDR message to stdout

Filtering is keyword-based using the vault note:
- `002 - research/research interests.md`
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import urllib.request


HF_TRENDING_URL = "https://huggingface.co/papers/trending"

RESEARCH_INTERESTS_NOTE = "002 - research/research interests.md"

FALLBACK_KEYWORDS = [
    "large language model",
    "llm",
    "language model",
    "transformer",
    "reasoning",
    "agent",
    "agents",
    "tool use",
    "reinforcement learning",
    "rlhf",
    "rlaif",
    "group relative policy optimization",
    "group relative policy optimisation",
    "grpo",
    "verifiable rewards",
    "rlvr",
    "parameter efficient fine tuning",
    "peft",
    "low rank adaptation",
    "lora",
]

HIGH_SIGNAL = {
    "grpo",
    "rlvr",
    "verifiable rewards",
    "group relative policy optimization",
    "group relative policy optimisation",
    "lora",
    "peft",
}


@dataclass
class Paper:
    title: str
    url: str
    abstract: str | None
    arxiv: str | None


def fetch(url: str, *, retries: int = 3, backoff_s: float = 2.0) -> str:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122 Safari/537.36",
        },
    )

    last_err: Exception | None = None
    for i in range(retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                return r.read().decode("utf-8", "ignore")
        except Exception as e:
            last_err = e
            if i < retries:
                import time

                time.sleep(backoff_s * (2**i))
                continue
            raise

    raise RuntimeError(str(last_err) if last_err else "fetch failed")


def norm(s: str) -> str:
    s = s.lower()
    s = s.replace("-", " ")
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def keyword_hit(text_norm: str, keyword: str) -> bool:
    k = norm(keyword)
    if not k:
        return False
    toks = [t for t in re.split(r"[^a-z0-9]+", k) if t]
    if len(toks) >= 2:
        return all(t in text_norm for t in toks)
    return k in text_norm


def load_interest_keywords(vault_root: Path) -> list[str]:
    p = vault_root / RESEARCH_INTERESTS_NOTE
    kws: list[str] = []

    if p.exists():
        txt = p.read_text(encoding="utf-8")
        for line in txt.splitlines():
            m = re.match(r"^\s*-\s+(.*)$", line)
            if not m:
                continue
            item = m.group(1).strip()
            if not item:
                continue
            kws.append(item)

            for par in re.findall(r"\(([^\)]+)\)", item):
                kws.append(par)

            if "reinforcement learning" in item.lower():
                kws.append("reinforcement learning")
                kws.append("rl")
            if "large language model" in item.lower() or "language model" in item.lower():
                kws.append("large language model")
                kws.append("llm")
            if "group relative policy" in item.lower():
                kws.append("grpo")
            if "low rank adaptation" in item.lower():
                kws.append("lora")
            if "parameter efficient" in item.lower():
                kws.append("peft")

    kws.extend(FALLBACK_KEYWORDS)

    out: list[str] = []
    seen = set()
    for k in kws:
        kn = norm(k)
        if not kn or kn in seen:
            continue
        seen.add(kn)
        out.append(k)

    return out


def interest_score(text: str, keywords: list[str]) -> int:
    t = norm(text)
    score = 0

    for k in HIGH_SIGNAL:
        if keyword_hit(t, k):
            score += 3

    for k in keywords:
        if keyword_hit(t, k):
            score += 1

    return score


def matches_interest(text: str, keywords: list[str]) -> bool:
    t = norm(text)
    if any(keyword_hit(t, k) for k in HIGH_SIGNAL):
        return True
    return interest_score(t, keywords) >= 2


def extract_arxiv_link(html: str) -> str | None:
    m = re.search(r"https?://arxiv\.org/abs/[0-9]{4}\.[0-9]{5}(v\d+)?", html)
    return m.group(0) if m else None


def arxiv_id_from_abs(url: str) -> str | None:
    m = re.search(r"arxiv\.org/abs/([0-9]{4}\.[0-9]{5})", url)
    return m.group(1) if m else None


def fetch_arxiv_meta(arxiv_id: str) -> tuple[str | None, str | None]:
    api = f"https://export.arxiv.org/api/query?id_list={arxiv_id}"
    try:
        xml = fetch(api)
    except Exception:
        return None, None

    titles = re.findall(r"<title>(.*?)</title>", xml, re.S)
    entry_title = None
    if len(titles) >= 2:
        entry_title = re.sub(r"\s+", " ", titles[1]).strip()

    s_m = re.search(r"<summary>(.*?)</summary>", xml, re.S)
    abstract = None
    if s_m:
        abstract = re.sub(r"\s+", " ", s_m.group(1)).strip()

    return entry_title, abstract


def extract_title(html: str) -> str | None:
    m = re.search(r"<meta[^>]+property=\"og:title\"[^>]+content=\"([^\"]+)\"", html)
    if m:
        return m.group(1)
    m = re.search(r"<title>(.*?)</title>", html, re.S)
    if m:
        return re.sub(r"\s+", " ", m.group(1)).strip()
    return None


def parse_trending(html: str, keywords: list[str]) -> list[Paper]:
    urls: list[str] = []
    for m in re.finditer(r"href=\"(/papers/[^\"]+)\"", html):
        u = "https://huggingface.co" + m.group(1)
        if u not in urls:
            urls.append(u)

    papers: list[Paper] = []
    for u in urls[:25]:
        try:
            ph = fetch(u, retries=1)
        except Exception:
            continue

        arxiv = extract_arxiv_link(ph)
        raw_title = extract_title(ph) or u

        pre_text = " ".join([raw_title, arxiv or ""])
        if not matches_interest(pre_text, keywords):
            continue

        arxiv_id = arxiv_id_from_abs(arxiv) if arxiv else None
        atitle, aabs = (None, None)
        if arxiv_id:
            atitle, aabs = fetch_arxiv_meta(arxiv_id)

        title = atitle or raw_title
        abstract = aabs
        if abstract is None:
            abs_m = re.search(r"<meta[^>]+name=\"description\"[^>]+content=\"([^\"]+)\"", ph)
            abstract = abs_m.group(1) if abs_m else None

        papers.append(Paper(title=title, url=u, abstract=abstract, arxiv=arxiv))

    return papers


def today_str() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def daily_note_path(vault_root: Path) -> Path:
    return vault_root / "000 - daily notes" / f"{today_str()}.md"


def short_summary(p: Paper) -> str:
    if p.abstract:
        s = re.sub(r"\s+", " ", p.abstract).strip()
        parts = re.split(r"(?<=[.!?])\s+", s)
        if parts and len(parts[0]) > 30:
            s = parts[0]
        if len(s) > 240:
            s = s[:240].rstrip() + "..."
        s = s.rstrip(".")
        return s
    return "summary pending"


def tldr_lines(papers: list[Paper]) -> list[str]:
    lines: list[str] = []
    for i, p in enumerate(papers, 1):
        ref = p.arxiv or p.url
        summ = short_summary(p)
        lines.append(f"{i}) {p.title} — {ref}")
        lines.append(f"summary: {summ}")
    return lines


def render_daily_note(papers: list[Paper]) -> str:
    d = today_str()
    out: list[str] = []
    out.append("---")
    out.append("tags:")
    out.append("- meta")
    out.append("description: ''")
    out.append("parent nodes:")
    out.append("- '[[research.base]]'")
    out.append("aliases: null")
    out.append("published on: null")
    out.append("---")
    out.append("")
    out.append(f"- Date: {d}")
    out.append("")
    out.append("## Latest papers")
    out.append("")
    if papers:
        for p in papers:
            ref = p.arxiv or p.url
            out.append(f"- [ ] [{p.title}]({ref})")
            out.append(f"\t- {short_summary(p)}")
    else:
        out.append("- [ ] none matched")
    out.append("")
    out.append("## TLDR top papers")
    out.append("")
    if papers:
        for line in tldr_lines(papers[:10]):
            out.append(f"- [ ] {line}")
    else:
        out.append("- [ ] none")
    out.append("")
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--vault", required=True, help="Path to vault repo root")
    args = ap.parse_args()

    vault_root = Path(args.vault).resolve()

    keywords = load_interest_keywords(vault_root)

    cache_dir = vault_root / ".cache"
    cache_dir.mkdir(exist_ok=True)
    trending_cache = cache_dir / "hf_trending.html"

    try:
        trending = fetch(HF_TRENDING_URL, retries=2)
        trending_cache.write_text(trending, encoding="utf-8")
    except Exception:
        if trending_cache.exists():
            trending = trending_cache.read_text(encoding="utf-8")
        else:
            sys.stdout.write(
                f"Daily papers ({today_str()})\n\nHugging Face is rate-limiting or unreachable, no update produced\n"
            )
            return 0

    papers = parse_trending(trending, keywords)

    scored = []
    for p in papers:
        if not p.arxiv:
            continue
        text = " ".join([p.title, p.abstract or "", p.arxiv or ""])
        scored.append((interest_score(text, keywords), p))

    scored.sort(key=lambda x: x[0], reverse=True)
    filtered = [p for _, p in scored[:20]]

    note_path = daily_note_path(vault_root)
    note_path.parent.mkdir(parents=True, exist_ok=True)
    note_path.write_text(render_daily_note(filtered), encoding="utf-8")

    msg: list[str] = []
    msg.append(f"{today_str()} (Europe/Amsterdam)")
    msg.append("")
    if filtered:
        msg.append("TLDR (filtered to research interests)")
        for i, p in enumerate(filtered[:10], 1):
            ref = p.arxiv or p.url
            msg.append(f"{i}) {p.title} — {ref}")
            msg.append(f"- {short_summary(p)}")
    else:
        msg.append("No trending papers matched current interests")

    sys.stdout.write("\n".join(msg) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
