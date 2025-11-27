---
title: 'Osaka Mainnet Testing'
date: 2025-11-27
author: Felix
description: "How execution-specs is testing Osaka on mainnet"
---

<div class="blog-metadata" markdown>
:material-account: **Felix** · :material-calendar: November 27, 2025 · :material-clock-outline: 5 min read
</div>

This post provides an overview of which execution-specs tests will be run on mainnet to verify the Osaka hard fork, similar to the [semi-manual testing effort for Prague](https://notes.ethereum.org/@marioevz/pectra-mainnet-testing).

## Summary

* Test transactions will be sent to mainnet for each EIP using EEST’s `execute` subcommands.
* All tests combined are expected to cost less than 0.1 ETH.
* The tests focus on blobs, modexp and p256verify.

## Schedule

* Tests will be run as soon as Osaka is activated.

## Test Spec

* Tests run via `execute remote` are stored as `test_eip_mainnet.py` under [this STEEL folder](https://github.com/ethereum/execution-specs/tree/forks/osaka/tests/osaka).
* Blob tests are dynamically run via `execute blob-sender` and do not require their own Python files.

## EIP-7594 (PeerDAS)

### Description

* Send transactions that contain one or multiple (up to six) blobs.

### Command

```bash
uv run execute blob-sender -v -s --fork=Osaka --rpc-seed-key=<put-here> \
--rpc-endpoint=<put-here> --chain-id=1 --eest-log-level=INFO \
--blob-seed=5 --blob-amount=3
```

### Transaction Hashes

* TODO: will be added here

### Outcome

* TODO: will be added here

## EIP-7883 (ModEXP)

### Description

* Five test cases for ensuring new gas cost formula is correctly implemented by clients.

### Command

```bash
uv run execute remote --tx-wait-timeout=600 \
--sender-funding-txs-gas-price=1000000000 \
--rpc-seed-key=<put-here> --rpc-endpoint=<put-here> \
--eoa-fund-amount-default=100000000000000000 \
--chain-id=1 --fork=osaka \
./tests/osaka/eip7883_modexp_gas_increase/test_eip_mainnet.py \
-v -s --eest-log-level=INFO
```

### Transaction Hashes

* TODO: will be added here

### Outcome

* TODO: will be added here

## EIP-7951 (P256Verify)

### Description

* Two test cases for ensuring that P256Verify has been correctly implemented. Includes a negative test that uses a signature that is valid only on secp256k1.

### Command

```bash
uv run execute remote --tx-wait-timeout=600 \
--sender-funding-txs-gas-price=1000000000 \
--rpc-seed-key=<put-here> --rpc-endpoint=<put-here> \
--eoa-fund-amount-default=100000000000000000 \
--chain-id=1 --fork=osaka \
./tests/osaka/eip7951_p256verify_precompiles/test_eip_mainnet.py \
-v -s --eest-log-level=INFO
```

### Transaction Hashes

* TODO: will be added here

### Outcome

* TODO: will be added here
