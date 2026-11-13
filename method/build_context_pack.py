#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build exact source excerpts with provenance; no semantic completeness claim.

Usage:
  python method/build_context_pack.py SPEC OUT_DIR
  python method/build_context_pack.py SPEC OUT_DIR --overwrite
  python method/build_context_pack.py --check OUT_DIR

SPEC lines (paths relative to repository root):
  current_canon.md|1|40|description
  current_canon.md|heading|exact heading text without hashes|description
Numeric end beyond EOF is clamped for legacy specs. Heading matches must be
unique. Each output is <= 40,000 UTF-8 bytes including all metadata. Oversized
sections split at line boundaries; an oversized single line raises an error.
"""

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

MAX_BYTES = 40_000
ROOT = Path(__file__).resolve().parents[1]
HEADER = ("# 設定原文摘錄\n\n"
          "> 摘錄不代表全部設定；含義以主管原檔與適用時期為準。\n"
          "> 按 context_brief 的回查路線補讀；能回答問題就停。\n\n")


def sha(data):
    return hashlib.sha256(data).hexdigest()


def source_path(root, name):
    path = (root / name).resolve()
    if not path.is_relative_to(root.resolve()) or not path.is_file():
        raise ValueError(f"Source must be a file inside repository: {name}")
    return path


def headings(lines):
    """ATX headings outside Markdown fenced blocks, with one-based lines."""
    found, fence = [], None
    for no, line in enumerate(lines, 1):
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})", line)
        if marker:
            mark = marker[1]
            if fence is None:
                fence = (mark[0], len(mark))
            elif mark[0] == fence[0] and len(mark) >= fence[1] and not line[marker.end():].strip():
                fence = None
            continue
        if fence:
            continue
        match = re.match(r"^ {0,3}(#{1,6})[ \t]+(.+?)\s*$", line)
        if match:
            title = re.sub(r"[ \t]+#+$", "", match[2]).strip()
            found.append((no, len(match[1]), title))
    return found


def selected_range(lines, kind, end):
    if kind == "heading":
        hs = headings(lines)
        hits = [(n, depth) for n, depth, title in hs if title == end]
        if len(hits) != 1:
            raise ValueError(f"Heading must match exactly once: {end!r} ({len(hits)} matches)")
        start, depth = hits[0]
        stop = next((n - 1 for n, d, _ in hs if n > start and d <= depth), len(lines))
        return start, stop
    start, stop = int(kind), min(int(end), len(lines))
    if not 1 <= start <= stop:
        raise ValueError(f"Invalid source range: {kind}..{end}")
    return start, stop


def git_commit(root):
    result = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"],
                            capture_output=True, text=True, check=False)
    return result.stdout.strip() if result.returncode == 0 else None


def build(spec_path, root=ROOT, max_bytes=MAX_BYTES):
    root = Path(root).resolve()
    raw_spec = Path(spec_path).read_bytes()
    commit = git_commit(root)
    pieces, selections, sources = [], [], {}
    for no, raw in enumerate(raw_spec.decode("utf-8-sig").splitlines(), 1):
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        fields = [x.strip() for x in raw.split("|", 3)]
        if len(fields) != 4:
            raise ValueError(f"SPEC line {no}: expected four fields")
        name, kind, end, desc = fields
        path = source_path(root, name)
        name = path.relative_to(root).as_posix()
        data = path.read_bytes()
        # Normalize CRLF as the previous tool did; preserve source line content.
        lines = data.decode("utf-8-sig").replace("\r\n", "\n").splitlines(keepends=True)
        start, stop = selected_range(lines, kind, end)
        digest = sha(data)
        sources[name] = digest
        selections.append({"path": name, "start": start, "end": stop,
                           "selector": [kind, end], "description": desc})
        hs = [title for n, _, title in headings(lines) if n <= start]
        title = hs[-1] if hs else "file start"

        def block(a, b):
            label = (f"---\n\n## {name} | L{a}–L{b} | {desc}\n"
                     f"Source heading: {title}\n"
                     f"Source HEAD: {commit or 'unavailable'}; file SHA-256: {digest}\n\n")
            return label + "".join(lines[a-1:b]) + "\n"

        a = start
        while a <= stop:
            b = a
            if len((HEADER + block(a, b)).encode("utf-8")) > max_bytes:
                raise ValueError(f"Single line plus metadata exceeds {max_bytes} bytes: {name}:{a}")
            while b < stop and len((HEADER + block(a, b+1)).encode("utf-8")) <= max_bytes:
                b += 1
            pieces.append(block(a, b))
            a = b + 1
    if not selections:
        raise ValueError("SPEC contains no excerpts")
    parts, current = [], HEADER
    for piece in pieces:
        if len((current + piece).encode("utf-8")) > max_bytes:
            parts.append(current)
            current = HEADER
        current += piece
    if current != HEADER:
        parts.append(current)
    manifest = {"format": 1, "source_head": commit, "spec_sha256": sha(raw_spec),
                "spec_text": raw_spec.decode("utf-8-sig"), "sources": sources,
                "selections": selections,
                "note": "File hashes describe actual inputs, including any uncommitted changes. Line endings normalized to LF. Semantic coverage is reviewed by a person/agent."}
    return parts, manifest


def write_pack(spec_path, out_dir, root=ROOT, overwrite=False, max_bytes=MAX_BYTES):
    parts, manifest = build(spec_path, root, max_bytes)
    out = Path(out_dir).resolve()
    existing = list(out.glob("context_pack_*.md")) if out.exists() else []
    manifest_path = out / "context_pack_manifest.json"
    if (existing or manifest_path.exists()) and not overwrite:
        raise ValueError("Pack already exists; use a new directory or --overwrite")
    # Validate every deletion target before replacing generated outputs only.
    for old in existing:
        if old.is_symlink() or old.resolve().parent != out or not re.fullmatch(r"context_pack_[0-9]+\.md", old.name):
            raise ValueError(f"Unexpected output path: {old.name}")
    if manifest_path.is_symlink():
        raise ValueError("Manifest cannot be a symlink")
    out.mkdir(parents=True, exist_ok=True)
    manifest["outputs"] = {}
    for i, content in enumerate(parts, 1):
        name = f"context_pack_{i}.md"
        data = content.encode("utf-8")
        (out / name).write_bytes(data)
        manifest["outputs"][name] = {"sha256": sha(data), "bytes": len(data)}
    for old in existing:
        if old.name not in manifest["outputs"]:
            old.unlink()
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def check_pack(out_dir, root=ROOT):
    out, root = Path(out_dir).resolve(), Path(root).resolve()
    manifest = json.loads((out / "context_pack_manifest.json").read_text(encoding="utf-8"))
    errors = []
    for name, digest in manifest["sources"].items():
        try:
            if sha(source_path(root, name).read_bytes()) != digest:
                errors.append(f"Changed source: {name}")
        except (OSError, ValueError):
            errors.append(f"Missing/invalid source: {name}")
    for name, info in manifest["outputs"].items():
        if not re.fullmatch(r"context_pack_[0-9]+\.md", name):
            errors.append(f"Invalid pack name: {name}")
            continue
        path = out / name
        if path.is_symlink() or not path.is_file() or sha(path.read_bytes()) != info["sha256"]:
            errors.append(f"Missing/changed excerpt: {name}")
    expected = set(manifest["outputs"])
    if {p.name for p in out.glob("context_pack_*.md")} != expected:
        errors.append("Unexpected pack files; regenerate into a clean output directory")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spec", nargs="?")
    parser.add_argument("out_dir", nargs="?")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--check", metavar="OUT_DIR")
    args = parser.parse_args()
    try:
        if args.check:
            errors = check_pack(args.check)
            print("\n".join(errors) if errors else "Sources and excerpts unchanged; semantic coverage still needs review.")
            return int(bool(errors))
        if not args.spec or not args.out_dir:
            parser.error("SPEC and OUT_DIR are required, or use --check OUT_DIR")
        manifest = write_pack(args.spec, args.out_dir, overwrite=args.overwrite)
        for name, info in manifest["outputs"].items():
            print(f"{name}: {info['bytes']:,} bytes")
        return 0
    except (ValueError, OSError, KeyError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
