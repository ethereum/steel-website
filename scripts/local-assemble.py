#!/usr/bin/env -S uv run --script
"""Assemble the site locally for testing.

Builds the Zensical landing page, stages local doc artifacts, and runs the
assemble-docs pipeline. Optionally starts an HTTP server to view the result.

Usage:
    uv run scripts/local-assemble.py            # build only
    uv run scripts/local-assemble.py --serve     # build and serve on port 8000
    uv run scripts/local-assemble.py --serve -p 9000  # custom port
    uv run scripts/local-assemble.py --skip-zensical   # skip the zensical build
"""

from __future__ import annotations

import argparse
import http.server
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Mirrors the BRANCH_CONFIG and PRODUCT in deploy.yml. Only branches with local
# artifacts will be included in versions.json (the rest are skipped gracefully).
PRODUCT = "execution-specs"

BRANCH_CONFIG = """\
forks/amsterdam|Amsterdam
devnets/bal/4|bal-devnet-4
"""

DEFAULT_BRANCH = "forks/amsterdam"


def build_zensical(site_dir: Path) -> None:
    """Build the Zensical landing site."""
    print("=== Building Zensical site ===", flush=True)
    subprocess.run(
        ["uv", "run", "zensical", "build", "--clean"],
        cwd=REPO_ROOT,
        check=True,
    )
    print(f"Built to {site_dir}/\n")


def stage_local_artifacts(docs_dir: Path, product: str) -> list[str]:
    """Copy local artifacts into the docs staging directory under <product>/.

    Returns the list of branch paths that were staged.
    """
    print("=== Staging local artifacts ===")
    artifacts_dir = REPO_ROOT / "artifacts"
    staged = []

    if not artifacts_dir.is_dir():
        print(f"No artifacts directory at {artifacts_dir}.")
        return staged

    # Each artifact directory is named branch_safe (e.g. forks-amsterdam) and
    # contains the branch content at <branch_path>/ inside it.
    for artifact in sorted(artifacts_dir.iterdir()):
        if not artifact.is_dir() or artifact.name.startswith("."):
            continue

        # Find the branch content directory inside the artifact.
        # The artifact has the structure: artifact/<branch_path>/...
        # e.g. forks-amsterdam/forks/amsterdam/index.html
        branch_dir = _find_branch_content(artifact)
        if not branch_dir:
            print(f"  Skipping {artifact.name} (no content found).")
            continue

        # Derive the branch path from the directory structure.
        branch_path = str(branch_dir.relative_to(artifact))
        dest = docs_dir / product / branch_path

        print(f"  {artifact.name} -> docs/{product}/{branch_path}/")
        if dest.exists():
            shutil.rmtree(dest)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(branch_dir, dest)
        staged.append(branch_path)

    print(f"Staged {len(staged)} branch(es).\n")
    return staged


def _find_branch_content(artifact_dir: Path) -> Path | None:
    """Find the branch root directory inside an artifact.

    The artifact contains the branch content nested at its branch path, e.g.
    artifacts/forks-amsterdam/forks/amsterdam/index.html. We find the
    shallowest directory containing index.html (closest to the artifact root).
    """
    candidates = list(artifact_dir.rglob("index.html"))
    if not candidates:
        return None
    return min(candidates, key=lambda p: len(p.parts)).parent


def run_assemble(docs_dir: Path) -> None:
    """Run assemble-docs.py on the staged docs directory."""
    print("=== Running assemble-docs ===\n", flush=True)
    script = REPO_ROOT / "scripts" / "assemble-docs.py"
    subprocess.run(
        [
            "uv",
            "run",
            str(script),
            str(docs_dir),
            "--product",
            PRODUCT,
            "--branch-config",
            BRANCH_CONFIG,
            "--default-branch",
            DEFAULT_BRANCH,
        ],
        cwd=REPO_ROOT,
        check=True,
    )
    print()


def serve(site_dir: Path, port: int) -> None:
    """Start a local HTTP server."""
    print(f"Serving {site_dir}/ at http://localhost:{port}")
    print("URLs to test:")
    print(f"  http://localhost:{port}/docs/                        (landing page)")
    print(f"  http://localhost:{port}/docs/versions.json           (versions)")
    print(f"  http://localhost:{port}/docs/{PRODUCT}/              (permalink)")
    print(f"  http://localhost:{port}/docs/{PRODUCT}/{DEFAULT_BRANCH}/  (docs + selector)")
    print()

    handler = http.server.SimpleHTTPRequestHandler
    server = http.server.HTTPServer(("", port), handler)
    import os

    os.chdir(site_dir)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--serve", action="store_true", help="Start HTTP server after building.")
    parser.add_argument("-p", "--port", type=int, default=8000, help="Port for HTTP server (default: 8000).")
    parser.add_argument("--skip-zensical", action="store_true", help="Skip the Zensical site build.")
    args = parser.parse_args()

    site_dir = REPO_ROOT / "site"
    docs_dir = site_dir / "docs"

    # 1. Build the Zensical landing site.
    if not args.skip_zensical:
        build_zensical(site_dir)
    else:
        print("=== Skipping Zensical build ===\n")
        site_dir.mkdir(parents=True, exist_ok=True)

    # 2. Stage local artifacts.
    docs_dir.mkdir(parents=True, exist_ok=True)
    staged = stage_local_artifacts(docs_dir, PRODUCT)
    if not staged:
        print("WARNING: No artifacts staged. The docs section will be empty.")

    # 3. Run assembly (inject selector, gen versions.json, gen redirects).
    run_assemble(docs_dir)

    # 4. Add .nojekyll.
    (site_dir / ".nojekyll").touch()

    print(f"Site assembled at {site_dir}/")
    total_size = sum(f.stat().st_size for f in site_dir.rglob("*") if f.is_file())
    print(f"Total size: {total_size / (1024 * 1024):.1f} MB\n")

    if args.serve:
        serve(site_dir, args.port)
    else:
        print("To serve locally:")
        print(f"  uv run scripts/local-assemble.py --serve")


if __name__ == "__main__":
    main()
