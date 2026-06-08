#!/usr/bin/env -S uv run --script
"""Post-staging assembly for aggregated docs.

Runs after branch artifacts have been staged. The default branch is staged
directly at <product>/ (no <branch>/ segment); non-default branches stay at
<product>/<branch>/. Performs two operations in order:

1. Injects the custom version selector <script> tag into all HTML files.
2. Generates versions.json (flat array with url fields). The default
   branch's entry uses `version: "<product>"` and `url: "/docs/<product>/"`
   so external links survive the rollover from e.g. forks/amsterdam to
   forks/bogota.

Usage (from repo root):
    uv run scripts/assemble-docs.py site/docs \\
        --product execution-specs \\
        --branch-config "forks/amsterdam|Amsterdam" \\
        --default-branch forks/amsterdam
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_TAG = '<script src="/docs/assets/version-selector.js"></script>'


def parse_branch_config(raw: str) -> list[tuple[str, str]]:
    """Parse 'path|label' lines into (path, label) tuples."""
    entries = []
    for line in raw.strip().splitlines():
        line = line.strip()
        if not line or "|" not in line:
            continue
        path, label = line.split("|", 1)
        entries.append((path.strip(), label.strip()))
    return entries


def inject_version_selector(docs_dir: Path, product: str) -> int:
    """Copy version-selector.js and inject a <script> tag into product HTML files"""
    scripts_dir = Path(__file__).resolve().parent
    src = scripts_dir / "version-selector.js"
    if not src.exists():
        print(f"ERROR: {src} not found", file=sys.stderr)
        return 0

    dest = docs_dir / "assets" / "version-selector.js"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(src.read_text())
    print(f"Copied {src.name} to {dest.relative_to(docs_dir)}")

    count = 0
    for html_file in (docs_dir / product).rglob("*.html"):
        content = html_file.read_text()
        if "</body>" in content and SCRIPT_TAG not in content:
            html_file.write_text(content.replace("</body>", f"{SCRIPT_TAG}</body>"))
            count += 1

    print(f"Injected version selector into {count} HTML files.")
    return count


def generate_versions_json(
    docs_dir: Path,
    product: str,
    branches: list[tuple[str, str]],
    default_branch: str,
) -> Path:
    """Generate versions.json as a flat array with url fields.

    Each entry's `version` field is the URL-path segment after /docs/, so
    version-selector.js can match it with a simple startsWith against
    location.pathname. The default branch's version is just `<product>`
    because it is deployed at /docs/<product>/ directly; non-default
    branches use `<product>/<branch>`.
    """
    versions = []
    for path, label in branches:
        if path == default_branch:
            if not (docs_dir / product / "index.html").is_file():
                print(f"  Skipping default branch {path} ({product}/index.html not found).")
                continue
            version_path = product
            url = f"/docs/{product}/"
            aliases = ["latest"]
        else:
            if not (docs_dir / product / path).is_dir():
                print(f"  Skipping {product}/{path} (directory not found).")
                continue
            version_path = f"{product}/{path}"
            url = f"/docs/{product}/{path}/"
            aliases = []
        versions.append(
            {
                "version": version_path,
                "title": label,
                "aliases": aliases,
                "url": url,
            }
        )

    out = docs_dir / "versions.json"
    out.write_text(json.dumps(versions, indent=2) + "\n")
    print(f"Generated {out.name} with {len(versions)} version(s):")
    for v in versions:
        tag = " (default)" if "latest" in v["aliases"] else ""
        print(f"  {v['version']}: {v['title']}{tag}")
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("docs_dir", type=Path, help="Path to the staged docs directory (e.g. site/docs).")
    parser.add_argument("--product", required=True, help="Product namespace (e.g. execution-specs).")
    parser.add_argument("--branch-config", required=True, help="Branch config lines (path|label), newline-separated.")
    parser.add_argument("--default-branch", required=True, help="Default branch path within the product (e.g. forks/amsterdam).")
    args = parser.parse_args()

    docs_dir = args.docs_dir.resolve()
    if not docs_dir.is_dir():
        print(f"ERROR: {docs_dir} is not a directory.", file=sys.stderr)
        sys.exit(1)

    branches = parse_branch_config(args.branch_config)
    if not branches:
        print("ERROR: No branches parsed from --branch-config.", file=sys.stderr)
        sys.exit(1)

    print(f"=== Assembling docs in {docs_dir} (product: {args.product}) ===\n")

    # 1. Inject version selector.
    inject_version_selector(docs_dir, args.product)
    print()

    # 2. Generate versions.json.
    generate_versions_json(docs_dir, args.product, branches, args.default_branch)
    print()

    print("Assembly complete.")


if __name__ == "__main__":
    main()
