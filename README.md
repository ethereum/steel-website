# Specs Team Website

This repository contains the [Zensical](https://zensical.org)-based website of the Ethereum Foundation Specs team (Specs [EL] and Specs [CL]), formerly STEEL. It is served at <https://steel.ethereum.foundation/>.

## Prerequisites

1. [uv](https://docs.astral.sh/uv/) manages Python and the dependencies:

    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

2. [just](https://just.systems/) runs the common tasks, locally and in CI:

    ```bash
    uv tool install --exclude-newer "10 days" rust-just
    just shell-completions
    ```

    For other ways to install `just`, see its [installation docs](https://just.systems/man/en/packages.html). CI uses `just` 1.46 and uv 0.13.4 (set in `.github/actions/setup-uv/action.yaml`) and the Python version in `.python-version`.

3. [lychee](https://lychee.cli.rs/), for `just check-links`. Any install method works, for example:

    ```bash
    brew install lychee      # or: cargo install lychee
    ```

    Prebuilt binaries: [lychee releases](https://github.com/lycheeverse/lychee/releases). CI uses lychee 0.24.2 (set in `.github/workflows/test.yml`).

## Usage

Serve the site locally with live reload:

```bash
just serve
```

List all recipes:

```bash
just
```

## Verifying local changes

Run the same checks as CI:

```bash
just static
just build
just check-links
```

| Recipe | What it does |
| --- | --- |
| `just static` | All static checks in parallel: `lock-check`, `spellcheck` and `lint-actions` |
| `just lock-check` | Check that `uv.lock` is up to date |
| `just spellcheck` | Spellcheck `docs/` with codespell; add false positives with `just whitelist <word>` |
| `just lint-actions` | Lint the GitHub Actions workflows with actionlint and shellcheck |
| `just build` | Build the site into `site/` with `zensical build --strict` |
| `just check-links` | Check that every link and image in the built `site/` points at a file that exists; run `just build` first (needs lychee). `zensical build --strict` checks links to pages and anchors but not images. External links are not checked |
| `just assemble` | Build the site and stage local execution-specs docs artifacts from `artifacts/`, as the deploy does (`--serve` to serve it) |
| `just clean` | Remove `site/` and `.cache/` |
