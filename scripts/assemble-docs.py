#!/usr/bin/env -S uv run --script
"""Post-staging assembly for aggregated docs.

Runs after branch artifacts have been staged into a docs directory. Performs
three operations in order:

1. Injects the custom version selector <script> tag into all HTML files.
2. Generates versions.json (flat array with url fields).
3. Generates redirect index.html files:
   - /docs/default/ and /docs/default/spec/ are stable permalinks that track
     the current default branch, so external links survive the rollover from
     e.g. forks/amsterdam to forks/bogota.
   - /docs/ and /docs/spec/ forward to those permalinks for backward compat.

Usage (from repo root):
    uv run scripts/assemble-docs.py site/docs \\
        --branch-config "forks/amsterdam|Amsterdam" \\
        --default-branch forks/amsterdam
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_TAG = '<script src="/docs/assets/version-selector.js"></script>'

REDIRECT_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta http-equiv="refresh" content="0; url={url}">
  <link rel="canonical" href="{url}">
  <title>Redirecting&hellip;</title>
</head>
<body>
  <p>Redirecting to <a href="{url}">{label}</a>.</p>
</body>
</html>
"""


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


def inject_version_selector(docs_dir: Path) -> int:
    """Copy version-selector.js and inject a <script> tag into all HTML files."""
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
    for html_file in docs_dir.rglob("*.html"):
        content = html_file.read_text()
        if "</body>" in content and SCRIPT_TAG not in content:
            html_file.write_text(content.replace("</body>", f"{SCRIPT_TAG}</body>"))
            count += 1

    print(f"Injected version selector into {count} HTML files.")
    return count


def generate_versions_json(
    docs_dir: Path,
    branches: list[tuple[str, str]],
    default_branch: str,
) -> Path:
    """Generate versions.json as a flat array with url fields."""
    versions = []
    for path, label in branches:
        if not (docs_dir / path).is_dir():
            print(f"  Skipping {path} (directory not found).")
            continue
        aliases = ["latest"] if path == default_branch else []
        versions.append(
            {
                "version": path,
                "title": label,
                "aliases": aliases,
                "url": f"/docs/{path}/",
            }
        )

    out = docs_dir / "versions.json"
    out.write_text(json.dumps(versions, indent=2) + "\n")
    print(f"Generated {out.name} with {len(versions)} version(s):")
    for v in versions:
        tag = " (default)" if v["version"] == default_branch else ""
        print(f"  {v['version']}: {v['title']}{tag}")
    return out


def generate_redirects(docs_dir: Path, default_branch: str) -> None:
    """Generate permalink redirects under docs/default/ and forwarders at docs root.

    /docs/default/ and /docs/default/spec/ are the stable permalinks — they
    track the current default branch and survive its rollover. /docs/ and
    /docs/spec/ forward through the permalinks so the old URLs keep working.
    """
    branch_url = f"/docs/{default_branch}/"
    branch_spec_url = f"/docs/{default_branch}/specs/reference/"
    targets = [
        # Permalinks: /docs/default/... -> current default branch.
        (docs_dir / "default" / "index.html", branch_url, default_branch),
        (
            docs_dir / "default" / "spec" / "index.html",
            branch_spec_url,
            f"{default_branch}/specs/reference",
        ),
        # Forwarders: /docs/ and /docs/spec/ -> /docs/default/...
        (docs_dir / "index.html", "/docs/default/", "default"),
        (docs_dir / "spec" / "index.html", "/docs/default/spec/", "default/spec"),
    ]
    for dest, url, label in targets:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(REDIRECT_TEMPLATE.format(url=url, label=label))
        print(f"Generated redirect: {dest.relative_to(docs_dir)} -> {url}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("docs_dir", type=Path, help="Path to the staged docs directory (e.g. site/docs).")
    parser.add_argument("--branch-config", required=True, help="Branch config lines (path|label), newline-separated.")
    parser.add_argument("--default-branch", required=True, help="Default branch path (e.g. forks/amsterdam).")
    args = parser.parse_args()

    docs_dir = args.docs_dir.resolve()
    if not docs_dir.is_dir():
        print(f"ERROR: {docs_dir} is not a directory.", file=sys.stderr)
        sys.exit(1)

    branches = parse_branch_config(args.branch_config)
    if not branches:
        print("ERROR: No branches parsed from --branch-config.", file=sys.stderr)
        sys.exit(1)

    print(f"=== Assembling docs in {docs_dir} ===\n")

    # 1. Inject version selector (must run before redirects are written).
    inject_version_selector(docs_dir)
    print()

    # 2. Generate versions.json.
    generate_versions_json(docs_dir, branches, args.default_branch)
    print()

    # 3. Generate redirects (written last so they don't get the script tag).
    generate_redirects(docs_dir, args.default_branch)
    print()

    print("Assembly complete.")


if __name__ == "__main__":
    main()
