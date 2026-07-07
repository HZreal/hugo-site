#!/usr/bin/env python3
"""Download Feishu documents with feishu2md from a TSV manifest."""

from __future__ import annotations

import argparse
import csv
import os
import subprocess
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", default="feishu-export/links.tsv", help="TSV file: target_path<TAB>url")
    parser.add_argument("--output", default="/Users/huang/Downloads/feishu", help="download root directory")
    parser.add_argument(
        "--feishu2md",
        default="/Users/huang/Downloads/free_download_manager/feishu2md-v2.4.5-darwin-arm64/feishu2md",
        help="path to feishu2md binary",
    )
    parser.add_argument("--dry-run", action="store_true", help="print commands without executing")
    return parser.parse_args()


def read_manifest(path: Path) -> list[tuple[str, str]]:
    if not path.exists():
        raise FileNotFoundError(f"manifest not found: {path}")

    rows: list[tuple[str, str]] = []
    with path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.reader(fh, delimiter="\t")
        for lineno, row in enumerate(reader, 1):
            if not row or not row[0].strip() or row[0].lstrip().startswith("#"):
                continue
            if len(row) < 2 or not row[1].strip():
                raise ValueError(f"{path}:{lineno}: expected target_path<TAB>url")
            rows.append((row[0].strip().strip("/"), row[1].strip()))
    return rows


def main() -> int:
    args = parse_args()
    manifest = Path(args.manifest)
    output_root = Path(args.output)
    feishu2md = Path(args.feishu2md)

    if not feishu2md.exists():
        raise FileNotFoundError(f"feishu2md not found: {feishu2md}")

    rows = read_manifest(manifest)
    if not rows:
        print(f"No download entries in {manifest}", file=sys.stderr)
        return 1

    for target_path, url in rows:
        target_dir = output_root / target_path
        cmd = [str(feishu2md), "dl", "-o", str(target_dir), url]
        print("+ " + " ".join(cmd))
        if args.dry_run:
            continue
        target_dir.mkdir(parents=True, exist_ok=True)
        env = os.environ.copy()
        subprocess.run(cmd, check=True, env=env)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
