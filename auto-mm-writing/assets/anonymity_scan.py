#!/usr/bin/env python3
"""Anonymity scanner for auto-mm.

Usage:
    python anonymity_scan.py <pdf> <paper_dir> <lang> <out_json> [whitelist_path]

Arguments:
    <pdf>             path to the compiled paper PDF
    <paper_dir>       paper source directory (.tex / .bib will be scanned)
    <lang>            en | zh | both — selects pattern set
    <out_json>        where to write the JSON report
    [whitelist_path]  optional: one regex pattern per line; matches are skipped

Exit code 0 = clean. Exit code 1 = at least one hit (write submit.zip is blocked).

What it does NOT scan (intentional):
- .sty and .cls files — these are upstream template/style files; maintainer
  URLs/contacts inside them are not the team's identity.
- PDF /Producer and /Creator metadata fields — these are always populated by
  xelatex with engine version strings; they are not PII.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

# Pattern sets. Extend per-run via inputs/anonymity_extra.json (loaded below).
PATTERNS_EN = [
    r"\bUniversity of [A-Z][A-Za-z]+\b",
    r"\b[A-Z][a-z]+ University\b",
    r"\bProf\.?\s+[A-Z][a-z]+\b",
    r"\bDr\.?\s+[A-Z][a-z]+\b",
    r"/Users/[A-Za-z0-9_]+",
    r"/Volumes/[A-Za-z0-9_]+",
    r"/home/[A-Za-z0-9_]+",
    r"C:\\\\Users\\\\[A-Za-z0-9_]+",
    r"github\.com/[A-Za-z0-9_-]+/[A-Za-z0-9_.-]+",
    r"gitee\.com/[A-Za-z0-9_-]+/[A-Za-z0-9_.-]+",
]

PATTERNS_ZH = [
    r"姓\s*名[:：]?\s*\S+",
    r"学\s*校[:：]?\s*\S+",
    r"学\s*院[:：]?\s*\S+",
    r"指导老师[:：]?\s*\S+",
    r"指导教师[:：]?\s*\S+",
    r"导\s*师[:：]?\s*\S+",
    r"[一-鿿]{2,4}大学",
    r"[一-鿿]{2,4}学院",
    r"(?:^|[\s（(])教\s*授",
    r"(?:^|[\s（(])副教授",
    r"(?:^|[\s（(])讲\s*师",
]

# Files to scan as source. .sty and .cls are intentionally absent.
SOURCE_SUFFIXES = {".tex", ".bib"}

# PDF metadata fields to scan. Producer/Creator excluded by design.
METADATA_KEYS = (b"Author", b"Title", b"Subject", b"Keywords")


def load_extra_patterns(extra_path: Path) -> list[str]:
    if not extra_path.exists():
        return []
    try:
        data = json.loads(extra_path.read_text())
        if isinstance(data, list):
            out = []
            for entry in data:
                if isinstance(entry, str):
                    out.append(entry)
                elif isinstance(entry, dict) and "pattern" in entry:
                    out.append(entry["pattern"])
            return out
    except (json.JSONDecodeError, OSError):
        pass
    return []


def load_whitelist(wl_path: Path) -> list[re.Pattern]:
    if not wl_path.exists():
        return []
    patterns = []
    for line in wl_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        try:
            patterns.append(re.compile(line))
        except re.error:
            continue
    return patterns


def is_whitelisted(match_text: str, whitelist: list[re.Pattern]) -> bool:
    return any(p.search(match_text) for p in whitelist)


def scan_pdf(pdf_path: Path, patterns: list[str], whitelist: list[re.Pattern]) -> list[dict]:
    hits = []

    # Metadata (lazy import so the scanner can announce missing dep cleanly)
    try:
        from pdfminer.pdfparser import PDFParser
        from pdfminer.pdfdocument import PDFDocument
        from pdfminer.high_level import extract_text
    except ImportError:
        print("anonymity_scan: pdfminer.six is required (pip install pdfminer.six)", file=sys.stderr)
        sys.exit(2)

    with pdf_path.open("rb") as f:
        doc = PDFDocument(PDFParser(f))
        meta = doc.info[0] if doc.info else {}
        for key in METADATA_KEYS:
            val = meta.get(key, b"")
            if isinstance(val, bytes):
                val = val.decode(errors="ignore")
            val = (val or "").strip()
            if val and not is_whitelisted(val, whitelist):
                hits.append({"kind": "metadata", "field": key.decode(), "value": val})

    # Body
    text = extract_text(str(pdf_path))
    for pat in patterns:
        for m in re.finditer(pat, text):
            mtxt = m.group(0)
            if is_whitelisted(mtxt, whitelist):
                continue
            hits.append({"kind": "body", "pattern": pat, "match": mtxt[:140]})
    return hits


def scan_sources(paper_dir: Path, patterns: list[str], whitelist: list[re.Pattern]) -> list[dict]:
    hits = []
    for f in paper_dir.rglob("*"):
        if not f.is_file() or f.suffix.lower() not in SOURCE_SUFFIXES:
            continue
        try:
            text = f.read_text(errors="ignore")
        except OSError:
            continue
        for pat in patterns:
            for m in re.finditer(pat, text):
                mtxt = m.group(0)
                if is_whitelisted(mtxt, whitelist):
                    continue
                line_no = text[: m.start()].count("\n") + 1
                hits.append({
                    "kind": "source",
                    "file": str(f),
                    "line": line_no,
                    "pattern": pat,
                    "match": mtxt[:140],
                })
    return hits


def main(argv: list[str]) -> int:
    if len(argv) < 5:
        print(__doc__, file=sys.stderr)
        return 2

    pdf = Path(argv[1])
    paper_dir = Path(argv[2])
    lang = argv[3]
    out_json = Path(argv[4])
    wl_path = Path(argv[5]) if len(argv) > 5 else paper_dir.parent.parent / "anonymity_whitelist.txt"
    extra_path = paper_dir.parent.parent / "inputs" / "anonymity_extra.json"

    if not pdf.exists():
        print(f"anonymity_scan: PDF not found: {pdf}", file=sys.stderr)
        return 2
    if not paper_dir.exists():
        print(f"anonymity_scan: paper dir not found: {paper_dir}", file=sys.stderr)
        return 2

    if lang == "en":
        patterns = list(PATTERNS_EN)
    elif lang == "zh":
        patterns = list(PATTERNS_ZH)
    elif lang == "both":
        patterns = list(PATTERNS_EN) + list(PATTERNS_ZH)
    else:
        print(f"anonymity_scan: unknown lang '{lang}' (use en | zh | both)", file=sys.stderr)
        return 2

    patterns += load_extra_patterns(extra_path)
    whitelist = load_whitelist(wl_path)

    report = {
        "pdf": str(pdf),
        "paper_dir": str(paper_dir),
        "lang": lang,
        "whitelist_loaded_from": str(wl_path) if wl_path.exists() else None,
        "extra_patterns_loaded_from": str(extra_path) if extra_path.exists() else None,
        "metadata_and_body_hits": scan_pdf(pdf, patterns, whitelist),
        "source_hits": scan_sources(paper_dir, patterns, whitelist),
    }
    out_json.write_text(json.dumps(report, ensure_ascii=False, indent=2))
    n = len(report["metadata_and_body_hits"]) + len(report["source_hits"])
    print(f"anonymity_scan: {n} hits → {out_json}")
    return 1 if n > 0 else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
