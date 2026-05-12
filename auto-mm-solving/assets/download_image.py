#!/usr/bin/env python3
"""Download an image into a figure's sources/ folder and emit starter metadata.

Usage:
    python download_image.py \
        --url <URL> \
        --out runs/<slug>/stage2_solving/figures/<fig_id>/sources/candidate_NN.<ext> \
        [--note "..."] \
        [--user-agent "..."]

What it does:
1. Fetches the URL with a sane user-agent and timeout.
2. Verifies the response is actually an image (Content-Type or magic-bytes check).
3. Saves the bytes to --out.
4. Emits <out>.meta.json next to the file with: url, retrieved_at_utc, dimensions,
   bytes, format, http_status. The human fills in: title, creator, license,
   license_url, notes.

What it intentionally does NOT do:
- Classify the license (you must read the source page).
- Crop, resize, or convert. The user can run Pillow / ImageMagick separately.
- De-duplicate. If you download the same URL twice it writes twice.
- Honor robots.txt or rate-limit aggressively. The user is responsible for
  respecting source-site terms.

Exit codes:
    0 = downloaded successfully
    1 = HTTP error or non-image response
    2 = bad arguments / file already exists
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

DEFAULT_UA = "auto-mm-figure-sourcing/0.1 (+https://github.com/deafenken/auto-MM)"
IMAGE_MAGIC = {
    b"\x89PNG\r\n\x1a\n": "png",
    b"\xff\xd8\xff": "jpeg",
    b"GIF87a": "gif",
    b"GIF89a": "gif",
    b"RIFF": "webp",          # plus "WEBP" at offset 8
    b"\x00\x00\x01\x00": "ico",
    b"BM": "bmp",
    b"%PDF-": "pdf",          # also accepted for vector
}


def sniff_format(body: bytes) -> str | None:
    for sig, name in IMAGE_MAGIC.items():
        if body.startswith(sig):
            if name == "webp" and len(body) >= 12 and body[8:12] != b"WEBP":
                continue
            return name
    return None


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description="Download an image for a sourced figure")
    p.add_argument("--url", required=True, help="image URL")
    p.add_argument("--out", required=True, help="destination path (under sources/)")
    p.add_argument("--note", default="", help="one-line note saved into meta.json")
    p.add_argument("--user-agent", default=DEFAULT_UA, help="HTTP User-Agent header")
    p.add_argument("--timeout", type=float, default=30.0, help="seconds")
    p.add_argument("--no-meta", action="store_true", help="skip writing the .meta.json file")
    args = p.parse_args(argv)

    out_path = Path(args.out)
    if out_path.exists():
        print(f"download_image: refusing to overwrite {out_path}", file=sys.stderr)
        return 2

    out_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        import requests
    except ImportError:
        print("download_image: requests is required (pip install requests)", file=sys.stderr)
        return 2

    try:
        resp = requests.get(
            args.url,
            headers={"User-Agent": args.user_agent},
            timeout=args.timeout,
            allow_redirects=True,
            stream=False,
        )
    except requests.RequestException as e:
        print(f"download_image: HTTP error: {e}", file=sys.stderr)
        return 1

    status = resp.status_code
    ctype = resp.headers.get("Content-Type", "").lower()

    if not resp.ok:
        print(f"download_image: HTTP {status} from {args.url}", file=sys.stderr)
        return 1

    body = resp.content
    fmt = sniff_format(body) or ctype.split(";")[0].split("/")[-1] or "unknown"

    if "image" not in ctype and fmt not in IMAGE_MAGIC.values() and fmt != "pdf":
        print(f"download_image: response is not an image (content-type={ctype!r}, "
              f"magic={fmt}). Saved nothing.", file=sys.stderr)
        return 1

    out_path.write_bytes(body)

    width = height = None
    try:
        from PIL import Image
        from io import BytesIO
        img = Image.open(BytesIO(body))
        width, height = img.size
    except (ImportError, Exception):
        pass

    if not args.no_meta:
        meta = {
            "url": args.url,
            "retrieved_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
            "platform": "TBD — fill in from source page",
            "title": "TBD",
            "creator": "TBD",
            "license": "TBD — read source page; do NOT guess",
            "license_url": "TBD",
            "dimensions_px": [width, height] if width and height else None,
            "file_bytes": len(body),
            "format": fmt,
            "http_status": status,
            "content_type": ctype,
            "notes": args.note,
            "modifications_by_us": "none yet",
        }
        meta_path = out_path.with_suffix(out_path.suffix + ".meta.json")
        meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2))
        print(f"saved {out_path} ({len(body)} bytes, {fmt}, {width}x{height})")
        print(f"wrote {meta_path} — fill in title/creator/license before commit")
    else:
        print(f"saved {out_path} ({len(body)} bytes, {fmt}, {width}x{height})")

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
