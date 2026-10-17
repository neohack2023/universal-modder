"""Read-only Universal Modder field-note inventory for AIOS candidate evidence.

No external packages, no network calls, no durable authority assignment.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re

FIELDS = ("kind", "title", "game", "game_version", "platform", "engine", "route", "status", "date")
LINK_RE = re.compile(r"https?://[^\s)>'\"]+")


def frontmatter(text: str) -> dict[str, str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    result: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        match = re.match(r"^([a-z_]+):\s*(.*)$", line)
        if match:
            key, value = match.groups()
            if key in FIELDS:
                result[key] = value.strip().strip("'\"")
    return result


def inspect_note(path: Path, root: Path) -> dict:
    data = path.read_bytes()
    text = data.decode("utf-8")
    rel = path.relative_to(root).as_posix()
    meta = frontmatter(text)
    return {
        "source_kind": "upstream_field_note",
        "source_path": rel,
        "source_sha256": hashlib.sha256(data).hexdigest(),
        "metadata": meta,
        "cited_urls": sorted(set(LINK_RE.findall(text))),
        "evidence_state": "SOURCE_PINNED",
        "local_byte_observed": False,
        "runtime_verified": False,
        "promotion_status": "CANDIDATE_ONLY",
    }


def inventory(root: Path, game_filter: str = "") -> list[dict]:
    game_dir = root / "knowledge" / "games"
    if not game_dir.is_dir():
        raise FileNotFoundError(f"Missing field-note root: {game_dir}")
    records = []
    for path in sorted(game_dir.rglob("*.md")):
        if path.is_symlink():
            continue
        item = inspect_note(path, root)
        if game_filter and game_filter.casefold() not in (
            item["source_path"] + " " + str(item["metadata"])
        ).casefold():
            continue
        records.append(item)
    return records


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--game", default="", help="Case-insensitive metadata/path match")
    parser.add_argument("--out", type=Path, help="Write JSONL; default stdout")
    args = parser.parse_args()
    lines = [json.dumps(record, sort_keys=True, ensure_ascii=False) for record in inventory(args.root, args.game)]
    result = "\n".join(lines) + ("\n" if lines else "")
    if args.out:
        args.out.write_text(result, encoding="utf-8", newline="\n")
    else:
        print(result, end="")


if __name__ == "__main__":
    main()
