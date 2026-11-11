---
title: "STEEL and the consensus specs team are now Specs"
date: 2026-11-11
authors: [danceratopz]
description: "The Ethereum Foundation's execution layer and consensus layer specification teams have merged into one team, Specs, with two focus areas: Specs [EL] and Specs [CL]."
---

In July 2026, two Ethereum Foundation teams merged:

- **STEEL** (Specifications and Testing for the Ethereum Execution Layer), which maintains the execution layer specifications and tests in [ethereum/execution-specs](https://github.com/ethereum/execution-specs).
- **The consensus specs team**, which maintains the consensus layer specifications and reference tests in [ethereum/consensus-specs](https://github.com/ethereum/consensus-specs) and the [c-kzg-4844](https://github.com/ethereum/c-kzg-4844) library.

Together we are **Specs**: nine people, led by [Mario Vega](../../team.md#mario-vega) and [Justin Traglia](../../team.md#justin-traglia). For now most of us still work on one layer, so the team has two focus areas, [Specs [EL]](../../el.md) and [Specs [CL]](../../cl.md). We expect that line to blur.

## Why merge?

Ethereum's upgrades increasingly change both layers at once. Enshrined proposer-builder separation, fork-choice enforced inclusion lists (FOCIL), shorter slots and execution proofs all need changes to the consensus specs, the execution specs, the [Engine API](https://github.com/ethereum/execution-apis/tree/main/src/engine) between them, and both test suites. These changes are easier to get right when the people who write the specs and tests for both layers plan, review and test them together.

The two specs also have a lot in common. Both are written in executable Python, both generate the reference tests that clients run, and both ship releases that client teams depend on during every devnet and testnet. Sharing tooling, release practices and testing ideas makes both of them better. Cross-layer work has already started: [Specs as Models](2026-06-11_specs-as-models.md), written by a STEEL member, applied category-partition testing to the consensus specs.

## What changes

- **This website** now covers both layers. See [Specs [EL]](../../el.md) and [Specs [CL]](../../cl.md) for what each side maintains and how it releases. In time it will move to a new address; the current one will keep working.
- **Our email** is now <specs@ethereum.foundation>.
- **We coordinate** in the [ethspecs](https://github.com/ethspecs) GitHub organisation.

## What doesn't change

The repositories, releases and test formats stay where they are. Execution layer fixtures are still released from [ethereum/execution-specs](https://github.com/ethereum/execution-specs/releases), and consensus layer reference tests from [ethereum/consensus-specs](https://github.com/ethereum/consensus-specs/releases). Client teams don't need to change anything.
