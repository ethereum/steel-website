# Steel Team Website

This repository contains a simple [zensical](https://zensical.org)-based website for the Ethereum Foundation STEEL Team.

## Prerequisites

[uv](https://docs.astral.sh/uv/):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
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

The available environments can be listed via:

```bash
uvx tox -la
```

Outputs:

```bash
uv  # check uv.lock file is up-to-date
spellcheck  # spellcheck markdown
build  # build with zensical
```
