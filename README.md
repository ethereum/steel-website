# Steel Team Website

This repository contains a simple [zensical](https://zensical.org)-based website for the Ethereum Foundation STEEL Team.

## Prerequisites

1. [uv](https://docs.astral.sh/uv/):

    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

2. (Optional) [lychee](https://lychee.cli.rs/):

    ```bash
    cargo install lychee
    ```

## Usage

Serve the page locally:

```bash
uv run zensical serve
```

## Verifying local changes

Run the same checks as CI via:

```bash
uvx tox
```

**Note:** for the `check-links` environment, install `lychee`, see Prerequisites.

The available environments can be listed via:

```bash
uvx tox -la
```

Outputs:

```bash
uv           # check uv.lock file is up-to-date
spellcheck   # spellcheck markdown
build        # build with zensical
check-links  # check links; requires lychee
```
