---
title: Specs [CL]
description: Specs [CL] maintains the Ethereum consensus layer specifications, their reference tests and the c-kzg-4844 library.
---

# Specs [CL]

We maintain the specification of Ethereum's proof-of-stake consensus layer: the rules every beacon node must follow. Its main home is [ethereum/consensus-specs](https://github.com/ethereum/consensus-specs), a Markdown specification that is also executable Python (the _pyspec_). Each release of the specs comes with the reference tests that consensus layer clients run to check their implementations.

## What we maintain

| Project | What it is |
| --- | --- |
| [ethereum/consensus-specs](https://github.com/ethereum/consensus-specs) | The consensus layer specifications, organised by upgrade. Each upgrade specifies only what it changes from the previous one. Rendered at [ethereum.github.io/consensus-specs](https://ethereum.github.io/consensus-specs/). |
| [`eth-consensus-specs`](https://pypi.org/project/eth-consensus-specs/) on PyPI | The executable pyspec, built from the Markdown specs and published with every release. |
| Reference tests | Test vectors generated from the pyspec, attached to every [consensus-specs release](https://github.com/ethereum/consensus-specs/releases). They replace the archived [ethereum/consensus-spec-tests](https://github.com/ethereum/consensus-spec-tests). |
| [ethereum/c-kzg-4844](https://github.com/ethereum/c-kzg-4844) | A minimal C implementation of the KZG polynomial-commitment API used by [EIP-4844](https://eips.ethereum.org/EIPS/eip-4844) blobs and [EIP-7594](https://eips.ethereum.org/EIPS/eip-7594) (PeerDAS), with bindings for Rust, Go, Java, C#, Node.js, Python, Nim, Elixir and more. |

We also contribute to [ethereum/ssz-specs](https://github.com/ethereum/ssz-specs), the reference SSZ serialisation and Merkleization, and to the [Engine API](https://github.com/ethereum/execution-apis/tree/main/src/engine) and [EIPs](https://github.com/ethereum/EIPs) where consensus changes reach into the execution layer.

## How the specs are organised

The specs live in Markdown, with each upgrade in its own directory under [`specs/`](https://github.com/ethereum/consensus-specs/tree/master/specs):

- **Stable upgrades:** Phase0, Altair, Bellatrix, Capella, Deneb, Electra and Fulu. Fulu (PeerDAS) is live on mainnet.
- **Upgrades in development:** [Gloas](https://github.com/ethereum/consensus-specs/tree/master/specs/gloas), the consensus half of Glamsterdam, and [Heze](https://github.com/ethereum/consensus-specs/tree/master/specs/heze), the consensus half of Hegotá.
- **Features:** proposals that are not yet scheduled for an upgrade are developed in parallel under [`specs/_features/`](https://github.com/ethereum/consensus-specs/tree/master/specs/_features), then moved into an upgrade once client teams agree to include them.

A build step (`pysetup`) pulls the Python code blocks out of the Markdown and assembles an executable spec for each upgrade and preset (`mainnet` and `minimal`). The test suite runs against this pyspec. The same tests, run in a special mode, write out the reference test vectors.

## How we release

Releases are cut from `master` with a [release workflow](https://github.com/ethereum/consensus-specs/blob/master/.github/workflows/release.yml) that is run by hand:

1. A "Bump version to vX" pull request sets the new version in `pyproject.toml`.
2. The workflow tags the release and drafts release notes, grouped by upgrade and feature.
3. It generates the reference tests for every upgrade, the preset-independent `general` tests and the `minimal` and `mainnet` presets, and attaches them to the [GitHub release](https://github.com/ethereum/consensus-specs/releases) as `general.tar.gz`, `minimal.tar.gz` and `mainnet.tar.gz`.
4. It builds the pyspec and publishes it to [PyPI](https://pypi.org/project/eth-consensus-specs/).
5. A follow-up workflow generates the compliance tests and attaches `comptests.tar.gz`.

Versions follow semantic versioning with pre-release suffixes: a series of `alpha` releases while an upgrade's contents are still changing, then `beta` releases once they settle, then a stable release for the mainnet upgrade. Pre-releases come out every two to four weeks, to keep client teams' devnets in step with the specs. See the [releases page](https://github.com/ethereum/consensus-specs/releases) for the current version.

Nightly reference tests from `master` are available as artifacts of the [tests workflow](https://github.com/ethereum/consensus-specs/actions/workflows/tests.yml).

## Current focus

- **[Gloas](https://github.com/ethereum/consensus-specs/tree/master/specs/gloas)**: enshrined proposer-builder separation ([EIP-7732](https://eips.ethereum.org/EIPS/eip-7732)) and the other consensus changes scheduled for Glamsterdam.
- **[Heze](https://github.com/ethereum/consensus-specs/tree/master/specs/heze)**: fork-choice enforced inclusion lists, FOCIL ([EIP-7805](https://eips.ethereum.org/EIPS/eip-7805)), together with its Engine API changes.
- **Shorter slots**: moving the fork choice to millisecond time so that slot durations can shrink.
- **Features in research**, such as execution proofs ([EIP-8025](https://github.com/ethereum/consensus-specs/tree/master/specs/_features/eip8025)) and post-quantum signatures.
- **Tooling**: a faster, stricter pyspec build, linting and type checking of the generated spec, and reliable release automation.

## Resources

- Specs: [ethereum/consensus-specs](https://github.com/ethereum/consensus-specs), rendered at [ethereum.github.io/consensus-specs](https://ethereum.github.io/consensus-specs/).
- Releases and reference tests: [consensus-specs releases](https://github.com/ethereum/consensus-specs/releases).
- KZG library: [ethereum/c-kzg-4844](https://github.com/ethereum/c-kzg-4844).
- Related specifications: [beacon-APIs](https://github.com/ethereum/beacon-APIs), [builder-specs](https://github.com/ethereum/builder-specs) and the [Engine API](https://github.com/ethereum/execution-apis/tree/main/src/engine).
