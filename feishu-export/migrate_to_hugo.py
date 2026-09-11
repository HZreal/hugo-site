#!/usr/bin/env python3
"""Migrate feishu2md export folders into Hugo docs page bundles."""

from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path
from urllib.parse import unquote


DEFAULT_SOURCE = "/Users/huang/Downloads/feishu/学习笔记"
DEFAULT_DEST = "content/zh/docs"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default=DEFAULT_SOURCE, help="Feishu export root, e.g. .../学习笔记")
    parser.add_argument("--dest", default=DEFAULT_DEST, help="Hugo docs content directory")
    parser.add_argument("--clean", action="store_true", help="remove destination before migrating")
    parser.add_argument("--dry-run", action="store_true", help="print planned operations")
    return parser.parse_args()


def title_from_markdown(path: Path) -> str:
    text = path.read_text(encoding="utf-8", errors="ignore")
    for line in text.splitlines():
        match = re.match(r"^#\s+(.+?)\s*$", line)
        if match:
            return match.group(1).strip()
    return path.parent.name if path.stem else "未命名"


def front_matter(title: str, weight: int) -> str:
    escaped = title.replace('"', '\\"')
    return (
        "+++\n"
        f'title = "{escaped}"\n'
        f"weight = {weight}\n"
        'type = "docs"\n'
        'layout = "page"\n'
        "+++\n\n"
    )


def strip_matching_h1(body: str, title: str) -> str:
    lines = body.splitlines()
    if lines and lines[0].strip() == f"# {title}":
        lines = lines[1:]
        if lines and not lines[0].strip():
            lines = lines[1:]
    return "\n".join(lines).rstrip() + "\n"


def rewrite_image_links(body: str, source_root: Path) -> str:
    source_root_text = str(source_root)

    def replace(match: re.Match[str]) -> str:
        alt = match.group(1)
        raw = unquote(match.group(2))
        path = raw
        if path.startswith(source_root_text):
            path = path.split("/static/", 1)[-1]
        elif "/static/" in path:
            path = path.split("/static/", 1)[-1]
        else:
            return match.group(0)
        return f"![{alt}](static/{Path(path).name})"

    return re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", replace, body)


def write_page(src_md: Path, dest_md: Path, title: str, weight: int, source_root: Path, dry_run: bool) -> None:
    body = src_md.read_text(encoding="utf-8", errors="ignore")
    body = strip_matching_h1(body, title)
    body = rewrite_image_links(body, source_root)
    content = front_matter(title, weight) + body
    print(f"write {dest_md}")
    if dry_run:
        return
    dest_md.parent.mkdir(parents=True, exist_ok=True)
    dest_md.write_text(content, encoding="utf-8")


def copy_static(src_dir: Path, dest_dir: Path, dry_run: bool) -> None:
    static_dir = src_dir / "static"
    if not static_dir.exists():
        return
    target = dest_dir / "static"
    print(f"copy {static_dir} -> {target}")
    if dry_run:
        return
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(static_dir, target)


def visible_subdirs(path: Path) -> list[Path]:
    return sorted(
        [p for p in path.iterdir() if p.is_dir() and p.name != "static" and not p.name.startswith(".")],
        key=lambda p: p.name.lower(),
    )


def markdown_files(path: Path) -> list[Path]:
    return sorted([p for p in path.glob("*.md") if not p.name.startswith(".")], key=lambda p: p.name.lower())


def migrate_dir(src_dir: Path, dest_dir: Path, source_root: Path, weight: int, dry_run: bool) -> None:
    mds = markdown_files(src_dir)
    subdirs = visible_subdirs(src_dir)

    if mds:
        if len(mds) == 1:
            title = title_from_markdown(mds[0])
            target = dest_dir / ("_index.md" if subdirs else "index.md")
            write_page(mds[0], target, title, weight, source_root, dry_run)
            copy_static(src_dir, dest_dir, dry_run)
        else:
            section_title = src_dir.name if src_dir != source_root else "技术文档"
            write_section_index(dest_dir, section_title, weight, dry_run)
            for idx, md in enumerate(mds, 1):
                title = title_from_markdown(md)
                child_dir = dest_dir / safe_name(title)
                write_page(md, child_dir / "index.md", title, idx * 10, source_root, dry_run)
    elif subdirs or src_dir == source_root:
        section_title = src_dir.name if src_dir != source_root else "技术文档"
        write_section_index(dest_dir, section_title, weight, dry_run)

    for idx, child in enumerate(subdirs, 1):
        migrate_dir(child, dest_dir / child.name, source_root, idx * 10, dry_run)


def safe_name(value: str) -> str:
    return re.sub(r'[\\/:*?"<>|]+', "-", value).strip() or "untitled"


def write_section_index(dest_dir: Path, title: str, weight: int, dry_run: bool) -> None:
    target = dest_dir / "_index.md"
    print(f"write {target}")
    if dry_run:
        return
    dest_dir.mkdir(parents=True, exist_ok=True)
    target.write_text(front_matter(title, weight), encoding="utf-8")


def main() -> int:
    args = parse_args()
    source = Path(args.source).expanduser().resolve()
    dest = Path(args.dest)

    if not source.exists():
        raise FileNotFoundError(f"source not found: {source}")

    if args.clean and dest.exists():
        print(f"remove {dest}")
        if not args.dry_run:
            shutil.rmtree(dest)

    migrate_dir(source, dest, source, 10, args.dry_run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
