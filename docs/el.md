---
title: Specs [EL]
description: Specs [EL] maintains the Ethereum execution layer specifications (EELS), the execution layer test suite and the tools that run it against clients.
---

# Specs [EL]

Specs [EL] maintains the specification of Ethereum's execution layer and the tests that check clients against it. Both live in [ethereum/execution-specs](https://github.com/ethereum/execution-specs):

- **The specs (EELS)**: the Ethereum Execution Layer Specification, written in executable Python. It is both documentation and a reference implementation of the EVM and the state transition.
- **The tests**: a Python test framework and the test cases written with it. The tests run against the specs to produce test vectors (_fixtures_), which execution layer clients run to check their implementations.

Until 2025 the tests lived in their own repository, `ethereum/execution-spec-tests` (EEST). [The Weld](blog/posts/2025-11-04_weld_final.md) moved them into execution-specs so that a spec change and its tests land in the same pull request.

## What we maintain

### Specifications

- Maintain the execution layer specification as readable, executable Python.
- Help EIP authors prototype their proposals in the specs. An EIP needs a reference implementation in the specs before it can be considered for inclusion in a fork.
- Publish a diff between forks for every upgrade (for example, [MODEXP changes in Osaka](https://ethereum.github.io/execution-specs/diffs/prague/osaka/vm/precompiled_contracts/modexp.py.html)).
- Publish the specs as the [`ethereum-execution`](https://pypi.org/project/ethereum-execution/) package on PyPI.

### Tests

- Write test cases for every EIP in the next fork, and for the effort to scale the L1.
- Generate and release the consensus test fixtures that every execution layer client runs in CI.
- Write [benchmark tests](/docs/execution-specs/tests/benchmark/): computation- and state-heavy worst cases that help client teams prepare for higher gas limits.
- Write zkEVM and stateless witness tests for the zkEVM effort.
- Help client teams debug failing tests, and feed what we learn back into the specs and tests.

### Running tests against clients

- [Consume](/docs/execution-specs/running_tests/consume/): a family of [Hive](https://github.com/ethereum/hive) simulators that run fixtures against clients through the Engine API, RLP-encoded blocks at startup, or sync.
- [Execute](/docs/execution-specs/running_tests/execute/): runs tests as transactions on live networks and devnets, or in Hive.

The docs [compare all the ways to run tests](/docs/execution-specs/running_tests/running/).

### Libraries and tools

- [ethereum/ethereum-types](https://github.com/ethereum/ethereum-types): types used by the specs.
- [ethereum/ethereum-rlp](https://github.com/ethereum/ethereum-rlp): Recursive Length Prefix (RLP) serialisation, as used by the specs.
- [docc](https://github.com/SamWilsn/docc), and its Rust port [rdocc](https://github.com/ethspecs/rdocc): the documentation generator that renders the specs.
- `gentest`: generates a Python test case from a mainnet or devnet transaction hash.

## How the work is organised

execution-specs uses a branch per fork:

- **`mainnet`**: the specs of every fork that is live on mainnet.
- **`forks/<fork>`**: the fork under active development. It is merged into `mainnet` once the fork goes live.
- **`eips/<fork>/eip-<n>`**: one branch per EIP. It is merged into the fork branch once the EIP is confirmed for that fork.
- **`devnets/<feature>/<n>`**: the combination of EIPs that a devnet runs.

The [documentation](docs/index.md) is built for `mainnet` and for the fork in development.

## How we release

Test fixtures are released with a [release workflow](https://github.com/ethereum/execution-specs/blob/forks/bogota/.github/workflows/release_fixtures.yaml). A maintainer starts it for a feature and version. The workflow builds the fixtures and drafts a pre-release, and a maintainer reviews it and publishes it. Publishing also builds the Hive simulator images for that release. Each release has a tracking issue, and a nightly run rehearses the release.

| Release | What it contains |
| --- | --- |
| `tests@vX.Y.Z` | The fixtures every client should pass: all forks up to the one clients have on their main branch. Released when there are changes, often once or twice a week. |
| `tests-<feature>-devnet@vX.Y.Z` | Fixtures for an active devnet, for example Glamsterdam, FOCIL or Bogota devnets. Advisory, not required to pass. |
| `tests-benchmark@vX.Y.Z` | Benchmark fixtures at a range of gas limits. |
| `tests-zkevm@vX.Y.Z` | zkEVM and stateless witness fixtures. |
| `vX.Y.Z` | The [`ethereum-execution`](https://pypi.org/project/ethereum-execution/) specs package on PyPI. |

In `tests@vX.Y.Z`, X is the fork number, Y changes on a consensus-breaking change and Z on new tests or other changes. Clients can download the latest release with `uv run consume cache --input=tests@latest`. See [Releases](/docs/execution-specs/running_tests/releases/) for details.

## Current focus

- **[Glamsterdam](https://forkcast.org/upgrade/glamsterdam)**: finishing specs and tests for the Amsterdam execution layer upgrade as it moves from testnets to mainnet.
- **Hegotá**: specifying and testing the EIPs proposed for the Bogota execution layer upgrade, and the devnets that try them out, including FOCIL together with Specs [CL].
- **Scaling the L1**: benchmark and worst-case tests that help clients raise the gas limit safely, and test vectors for zkEVMs.
- **One test corpus**: bringing the remaining tests from [ethereum/tests](https://github.com/ethereum/tests) into the new framework, so that clients have one source of consensus tests and [retesteth](https://github.com/ethereum/retesteth) can retire.

## Resources

- Specs and tests: [ethereum/execution-specs](https://github.com/ethereum/execution-specs).
- [Specs documentation](/docs/execution-specs/specs/reference/src/ethereum/index.html).
- [Testing framework documentation](/docs/execution-specs/consensus_tests/).
- [Test case reference](/docs/execution-specs/tests/).
- [Fixture releases](https://github.com/ethereum/execution-specs/releases).
