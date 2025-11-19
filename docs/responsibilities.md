---
title: Responsibilities
---

STEEL's work is mainly centered around the [ethereum/execution-specs](https://github.com/ethereum/execution-specs) repository, which consists of:

- The Ethereum Execution Layer Specs (EELS) which are written in executable Python that serve as both documentation and a reference implementation.
- The Ethereum Execution Spec Tests (EEST) which generate and release consensus and benchmarking test vectors for client teams.

These are used to generated test vectors (aka fixtures) that can be executed against EL client implementations. The main purpose of EELS and EEST to ensure that Execution Layer upgrades are clearly specified, sufficiently tested, and safe for Mainnet deployment.

## Core Responsibilities

### Specifications (EELS)

- Maintain the Execution Layer specification as executable Python code.
- Help prototype and document proposed EIPs.
- Publish spec snapshot releases to highlight differences between forks (e.g., [MODEXP changes in Osaka](https://ethereum.github.io/execution-specs/diffs/prague/osaka/vm/precompiled_contracts/modexp.py.html)).
- Provide the reference EVM used to generate consensus tests for execution layer client teams.

### Tests (EEST)

- Maintain Python test cases for EIPs and "Scale the L1" efforts.
- Generate and continuously deliver reference test case releases for Execution Layer clients.
- Provide benchmarking and pathological test cases to help clients prepare for stress scenarios.
- Assist client teams in debugging failures and feed findings back into specs and tests.

### Libraries and Tooling

#### Libraries

- [ethereum/ethereum-types](https://github.com/ethereum/ethereum-types) - types used by Ethereum.
- [ethereum/ethereum-rlp](https://github.com/ethereum/ethereum-rlp) - Recursive-length prefix (RLP) serialization as used by the Ethereum Specification.
- [ethereum/web3.py](https://github.com/ethereum/web3.py) - A python interface for interacting with the Ethereum blockchain and ecosystem.

#### Client Test Frameworks

We maintain several system-test frameworks to help test Execution Layer Clients:

- [Consume](https://eest.ethereum.org/main/running_tests/consume/) - a family of [Hive](https://github.com/ethereum/hive) simulators that execute EEST vectors against clients by feeding blocks via RLP (upon startup) or the Engine API.
- [Execute](https://eest.ethereum.org/main/running_tests/execute/) - a framework for running EEST test vectors on live networks or as a Hive simulator, ensuring fixture compatibility across both simulated and real environments.

See the EEST docs [on running tests for an overview and comparison](https://eest.ethereum.org/main/running_tests/running/) of all Hive simulators and frameworks.

<br/>

#### Other Tooling

- [docc](https://github.com/SamWilsn/docc) - A documentation creation tool for Python with a specific focus on markdown and extensibility.
- [eth-tester](https://github.com/ethereum/eth-tester) - A tool suite for testing ethereum applications.
- [Blobber](https://github.com/marioevz/blobber) - A live-network tool for testing blob transaction propagation across clients.
- `gentest` - A utility that generates Python test cases directly from a Mainnet or devnet transaction hash, useful for reproducing real-world scenarios in the EEST framework.

## Collaboration

Our work is very collaborative in nature, we work closely with:

- **Researchers & EIP Authors** - to ensure proposals are clear, sufficient, and correct before inclusion.
- **Client Developers** - to verify implementations, provide debugging support, and ensure readiness before forks.
- **Security Researchers** - to harden specifications and tests against ambiguous or unsafe behavior.

## Current Focus

- **[Fusaka hard fork](https://forkcast.org/upgrade/fusaka)** - finalizing tests and specs in preparation for the Fusaka hard fork, scheduled for Nov 2025.
- **[Glamsterdam hard fork](https://forkcast.org/upgrade/glamsterdam)** - contributing to [Block-Level Access List](https://eips.ethereum.org/EIPS/eip-7928) (BAL) specs and tests.
- **Scale the L1** - generating computational- and state-intensive test cases to safely raise the block gas limit and test zkEVMs.
- **Test Corpus Unification** - enabling test vector generation from the corpus of tests from `ethereum/tests` (the predecessor to EEST) using EEST's test framework. The aim is to provide clients with a single source of consensus tests and deprecate the previous test framework [ethereum/retesteth](https://github.com/ethereum/retesteth).

## Resources

- EELS and EEST Repository: [ethereum/execution-specs](https://github.com/ethereum/execution-specs).
- [EELS Documentation](https://ethereum.github.io/execution-specs/).
- [EEST Tooling Documentation](https://eest.ethereum.org/main/).
- [EEST Test Case Documentation](https://eest.ethereum.org/main/tests).
- [Previous Presentations](https://github.com/ethsteel/presentations/blob/main/README.md).
