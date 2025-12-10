---
title: 'Osaka Mainnet Testing'
date: 2025-11-27
author: Felix
description: "How execution-specs tested Osaka on mainnet"
---

<div class="blog-metadata" markdown>
:material-account: **Felix, Mario** · :material-calendar: November 27, 2025 · :material-clock-outline: 5 min read
</div>

As part of the hard-fork verification process, the STEEL Team executes a subset of consensus tests from [ethereum/execution-specs](https://github.com/ethereum/execution-specs) directly on Ethereum mainnet - we're happy to report that all the tests selected for the Osaka hard fork passed!

In this post you can find details about which tests were executed and the corresponding transaction hashes. The corresponding semi-manual testing effort for Prague can be found [in this report](https://notes.ethereum.org/@marioevz/pectra-mainnet-testing).

## Summary

- Test transactions were sent to mainnet for each EIP using EELS's `execute` subcommands.
- All tests passed successfully with approximately ~0.0001 ETH gas used.
- The tests focused on ModExp changes, the transaction gas limit cap, CLZ opcode, and P256Verify.

## Schedule

- Fork Epoch: [411392](https://light-mainnet.beaconcha.in/epoch/411392) (`Dec-03-2025 09:49:11 PM UTC`).
- Fork Expected Finalization Epoch: [411394](https://light-mainnet.beaconcha.in/epoch/411394) (`Dec-03-2025 10:01:59 PM UTC`).
- Testing commenced at the fork finalization epoch after the chain finalized successfully.

## Test Specification

- Tests were run via `execute remote` from [ethereum/execution-specs@2b7dc12](https://github.com/ethereum/execution-specs/commit/2b7dc12d89bc9daa45a0737ab36c14fe55eaad5b).

### Included EIPs

- [EIP-7823: Set upper bounds for MODEXP](https://eips.ethereum.org/EIPS/eip-7823).
- [EIP-7825: Transaction Gas Limit Cap](https://eips.ethereum.org/EIPS/eip-7825).
- [EIP-7883: ModExp Gas Cost Increase](https://eips.ethereum.org/EIPS/eip-7883).
- [EIP-7910: eth_config JSON-RPC Method](https://eips.ethereum.org/EIPS/eip-7910).
- [EIP-7939: Count leading zeros (CLZ) opcode](https://eips.ethereum.org/EIPS/eip-7939).
- [EIP-7951: Precompile for secp256r1 Curve Support](https://eips.ethereum.org/EIPS/eip-7951).

### Excluded EIPs

The following EIPs were not testable via EL transactions:

- [EIP-7594: PeerDAS](https://eips.ethereum.org/EIPS/eip-7594) (Networking related, not testable via EL transactions).
- [EIP-7642: eth/69](https://eips.ethereum.org/EIPS/eip-7642) (Networking related, not testable via EL transactions).
- [EIP-7892: Blob Parameter Only ('BPO') Hardforks](https://eips.ethereum.org/EIPS/eip-7892) (Requires many blob transactions included in the same block, not easily achievable via `execute` command).
- [EIP-7917: Deterministic proposer lookahead](https://eips.ethereum.org/EIPS/eip-7917) (CL only change).
- [EIP-7918: Blob base fee bounded by execution cost](https://eips.ethereum.org/EIPS/eip-7918) (Environment dependent, not testable via `execute` command).
- [EIP-7934: RLP Execution Block Size Limit](https://eips.ethereum.org/EIPS/eip-7934) (Environment dependent, not testable via `execute` command).
- [EIP-7935: Set default gas limit to 60M](https://eips.ethereum.org/EIPS/eip-7935) (Environment dependent, not testable via `execute` command).

## EIP-7823 (ModEXP Upper Bound)

### Description

- Executed the pre-compile at the exact boundary and above the boundary.

### Command

```bash
uv run execute remote --fork=Osaka -m mainnet \
tests/osaka/eip7823_modexp_upper_bounds/test_eip_mainnet.py \
--rpc-seed-key $MAINNET_RPC_SEED_KEY \
--rpc-endpoint $MAINNET_RPC_ENDPOINT \
--chain-id $MAINNET_CHAIN_ID
```

### Transaction Hashes

| Test ID | Transaction Hash |
| ------- | ---------------- |
| `test_modexp_boundary[fork_Osaka-state_test-base-boundary-1024-bytes]` | [0x5be8356a...](https://etherscan.io/tx/0x5be8356abea4466ad03a1821d34b437b0b45e1b38c03b09cc545ddb36a0548b1) |
| `test_modexp_over_boundary[fork_Osaka-state_test-base-over-boundary-1025-bytes]` | [0x1eaf26a2...](https://etherscan.io/tx/0x1eaf26a250f50411888a11d227dbdfeecb51a273613cac9a9fa097b64b102b0f) |

### Outcome

:white_check_mark: **PASS** - 2/2 tests passed.

## EIP-7825 (Transaction Gas Limit Cap)

### Description

- Sent a transaction with the gas limit cap and above.

### Command

```bash
uv run execute remote --fork=Osaka -m mainnet \
tests/osaka/eip7825_transaction_gas_limit_cap/test_eip_mainnet.py \
--rpc-seed-key $MAINNET_RPC_SEED_KEY \
--rpc-endpoint $MAINNET_RPC_ENDPOINT \
--chain-id $MAINNET_CHAIN_ID
```

### Transaction Hashes

| Test ID | Transaction Hash |
| ------- | ---------------- |
| `test_tx_gas_limit_cap_at_maximum[fork_Osaka-state_test]` | [0x95275083...](https://etherscan.io/tx/0x952750833f1dab54ea088dc936f37c6064c0fb3678985d4351f17cca9b0c5ece) |
| `test_tx_gas_limit_cap_exceeded[fork_Osaka-state_test]` (funding) | [0xc5ac1131...](https://etherscan.io/tx/0xc5ac11315053776ac903235ef71f97deabe4ae9d5a4bd18b645e97699ecec2f6) |
| `test_tx_gas_limit_cap_exceeded[fork_Osaka-state_test]` (refund) | [0x46d32a99...](https://etherscan.io/tx/0x46d32a995a7934d268bc264c7a6e1c15308a73a07cc7c12e50a9ed21a383941b) |

Note: `test_tx_gas_limit_cap_exceeded` had no direct test transaction as expected (tx was rejected).

### Outcome

:white_check_mark: **PASS** - 2/2 tests passed.

## EIP-7883 (ModEXP Gas Repricing)

### Description

- Triggered the gas cost changes in the ModExp precompile with five test cases.

### Command

```bash
uv run execute remote --fork=Osaka -m mainnet \
tests/osaka/eip7883_modexp_gas_increase/test_eip_mainnet.py \
--rpc-seed-key $MAINNET_RPC_SEED_KEY \
--rpc-endpoint $MAINNET_RPC_ENDPOINT \
--chain-id $MAINNET_CHAIN_ID
```

### Transaction Hashes

| Test ID | Transaction Hash |
| ------- | ---------------- |
| `test_modexp_different_base_lengths[fork_Osaka-state_test-32-bytes-long-base]` | [0x26d0f8b5...](https://etherscan.io/tx/0x26d0f8b580d735ac74755030f8e4a52ed02814888887e64097c81c7d0f6dd2e0) |
| `test_modexp_different_base_lengths[fork_Osaka-state_test-33-bytes-long-base]` | [0x71470510...](https://etherscan.io/tx/0x71470510279c1006e84fc65c3977983ecdf9658a3aaca0f0e98b90914333e4e7) |
| `test_modexp_different_base_lengths[fork_Osaka-state_test-1024-bytes-long-exp]` | [0xca67e591...](https://etherscan.io/tx/0xca67e591a6f4d4f995ede0927c13e3713d9393660ff9b710fec548bbe6863a51) |
| `test_modexp_different_base_lengths[fork_Osaka-state_test-nagydani-1-pow0x10001]` | [0x10d904c6...](https://etherscan.io/tx/0x10d904c6c5d7f3e1f1f527b8871176faac26f4ebc92bdf4a767799fa0e446083) |
| `test_modexp_different_base_lengths[fork_Osaka-state_test-zero-exponent-64bytes]` | [0xf2ae6f73...](https://etherscan.io/tx/0xf2ae6f732cea8ff243d394790c68150118de7a13edcb3c839a848d1043e63189) |

### Outcome

:white_check_mark: **PASS** - 5/5 tests passed.

## EIP-7910 (eth_config JSON-RPC Method)

### Description

- Ran `execute eth-config` after the fork to validate remaining BPO forks.

### Command

```bash
uv run execute eth-config --network Mainnet \
--rpc-endpoint $MAINNET_RPC_ENDPOINT \
--chain-id=1
```

### Transaction Hashes

This was a regular call to a node's JSON RPC to request information; it did not require sending a transaction.

### Outcome

:white_check_mark: **PASS** - 6/6 tests passed against 5 mainnet RPC endpoints (Geth, Reth, Nethermind, Erigon, and Besu). All returned consistent results confirming correct `eth_config` implementation.

## EIP-7939 (CLZ)

### Description

- Executed the CLZ opcode with different inputs.

### Command

```bash
uv run execute remote --fork=Osaka -m mainnet \
tests/osaka/eip7939_count_leading_zeros/test_eip_mainnet.py \
--rpc-seed-key $MAINNET_RPC_SEED_KEY \
--rpc-endpoint $MAINNET_RPC_ENDPOINT \
--chain-id $MAINNET_CHAIN_ID
```

### Transaction Hashes

| Test ID | Transaction Hash |
| ------- | ---------------- |
| `test_clz_mainnet[fork_Osaka-state_test-clz-8-leading-zeros]` | [0x9ec7c2d9...](https://etherscan.io/tx/0x9ec7c2d94378ce3eaa9c794ce70d2f6f0288918d008bc8de79f167a008cb6437) |
| `test_clz_mainnet[fork_Osaka-state_test-clz-all-zeros]` | [0x7f9ea62c...](https://etherscan.io/tx/0x7f9ea62cf3490a0080523c056fb0327ee3de2d9a854e297b8fe86442d5126bb0) |

### Outcome

:white_check_mark: **PASS** - 2/2 tests passed.

## EIP-7951 (P256Verify)

### Description

- Executed the precompile with different inputs, including a negative test that used a signature valid only on secp256k1.

### Command

```bash
uv run execute remote --fork=Osaka -m mainnet \
tests/osaka/eip7951_p256verify_precompiles/test_eip_mainnet.py \
--rpc-seed-key $MAINNET_RPC_SEED_KEY \
--rpc-endpoint $MAINNET_RPC_ENDPOINT \
--chain-id $MAINNET_CHAIN_ID
```

### Transaction Hashes

| Test ID | Transaction Hash |
| ------- | ---------------- |
| `test_valid[fork_Osaka-state_test--valid_r1_sig-]` | [0x6911ce58...](https://etherscan.io/tx/0x6911ce5860e375b70c35a5b7d4860a85481e2c4e3db057196cd8089dc7434b92) |
| `test_invalid[fork_Osaka-state_test--invalid_r1_sig_but_valid_k1_sig-]` | [0x63e3c33f...](https://etherscan.io/tx/0x63e3c33f556f13df928c994cbe97e0cb7f5994912fc1c355d128027461d005de) |

### Outcome

:white_check_mark: **PASS** - 2/2 tests passed.
