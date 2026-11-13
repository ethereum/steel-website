---
title: About
description: The Ethereum Foundation Specs team maintains the specifications and reference tests for Ethereum's execution and consensus layers.
---

![Specs logo](assets/images/home/specs.svg){ .logo-light .about-logo }
![Specs logo](assets/images/home/specs-dark.svg){ .logo-dark .about-logo }

Specs is a team in [Ethereum Foundation Protocol](https://protocol.ethereum.foundation/). We maintain the specifications of Ethereum's execution and consensus layers and the tests that check clients against them:

- **[Specs [EL]](el.md)** maintains the execution layer specifications and their test suite in [ethereum/execution-specs](https://github.com/ethereum/execution-specs), and the tools that run those tests against execution clients.
- **[Specs [CL]](cl.md)** maintains the consensus layer specifications and their reference tests in [ethereum/consensus-specs](https://github.com/ethereum/consensus-specs), and the [c-kzg-4844](https://github.com/ethereum/c-kzg-4844) library.

The specifications of both layers are written as executable Python, and we generate the reference tests from them. Our priority is to make sure the next [network upgrade](https://forkcast.org/) is clearly specified and has thorough test coverage before it reaches mainnet. Alongside that, we help researchers turn proposals into specifications and tests for future upgrades, and we write the stress tests that help clients [scale the L1](/docs/execution-specs/tests/benchmark/) safely.

An upgrade changes both layers, and more and more EIPs touch both. Inclusion lists, enshrined proposer-builder separation, shorter slots and execution proofs all need the two specifications, the [Engine API](https://github.com/ethereum/execution-apis/tree/main/src/engine) between them and both test suites to change together. The team page lists [who we are](team.md).

## Who we work with

- **Researchers and EIP authors**: to make proposals clear, complete and correct before they are included in an upgrade.
- **Client teams** on both layers: to check implementations, help debug failures and get clients ready for each upgrade.
- **Other EF Protocol teams**: [ethPandaOps](https://ethpandaops.io/) on devnets and Hive, [Geth](https://geth.ethereum.org/), [zkEVM](https://zkevm.ethereum.foundation/) on execution proofs and zkEVM tests, [Cryptography](https://crypto.ethereum.org/) and [Post-Quantum](https://pq.ethereum.org/) on the move to quantum-safe signature schemes, [Security](https://security.ethereum.org/), and the state and finality teams on the parts of the specs they work on.

We coordinate in the [ethspecs](https://github.com/ethspecs) GitHub organisation, which holds our [project management](https://github.com/ethspecs/pm), [presentations](https://github.com/ethspecs/presentations) and shared tooling.

!!! success "Contact us"
    <specs@ethereum.foundation>

!!! danger "Reporting mainnet bugs"
    To find out how to disclose a vulnerability in Ethereum, visit [bounty.ethereum.org](https://bounty.ethereum.org) or email <bounty@ethereum.org>.

## From STEEL to Specs

Until July 2026 these were two teams. STEEL (Specifications and Testing for the Ethereum Execution Layer) maintained the execution layer specs and tests, and the consensus specs team maintained the consensus layer specs. To foster closer collaboration between the specification teams in the Ethereum Foundation, the two teams merged and are now known as **Specs**, with the sub-teams **Specs [EL]** and **Specs [CL]**. This site was STEEL's site, and older blog posts still use that name.
