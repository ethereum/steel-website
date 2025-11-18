---
title: 'Testing `eth_config`'
date: 2025-09-15
author: felix314159
description: "A brief summary of how we ensure that clients use the same configuration."
---

<div class="blog-metadata" markdown>
:material-account: **felix314159** · :material-calendar: September 15, 2025 · :material-clock-outline: 3 min read
</div>

## What is `eth_config`?

It is an RPC method that was introduced with [EIP-7910](https://eips.ethereum.org/EIPS/eip-7910) to allow requesting certain configuration data from clients. The goal of introducing the `eth_config` method is to prevent events such as the [Holešky incident](https://blog.sigmaprime.io/pectra-holesky-incident.html) from ever happening again.
<br/>
<br/>
Below shows an example response for a client running in fusaka-devnet-5:

```json
{
  "jsonrpc": "2.0",
  "result": {
    "current": {
      "activationTime": 1757906016,
      "blobSchedule": {
        "baseFeeUpdateFraction": 18361626,
        "max": 33,
        "target": 22
      },
      "chainId": "0x1a6bdadc0",
      "forkId": "0xaaf46a33",
      "precompiles": {
        "ECREC": "0x0000000000000000000000000000000000000001",
        "SHA256": "0x0000000000000000000000000000000000000002",
        "RIPEMD160": "0x0000000000000000000000000000000000000003",
        "ID": "0x0000000000000000000000000000000000000004",
        "MODEXP": "0x0000000000000000000000000000000000000005",
        "BN254_ADD": "0x0000000000000000000000000000000000000006",
        "BN254_MUL": "0x0000000000000000000000000000000000000007",
        "BN254_PAIRING": "0x0000000000000000000000000000000000000008",
        "BLAKE2F": "0x0000000000000000000000000000000000000009",
        "KZG_POINT_EVALUATION": "0x000000000000000000000000000000000000000a",
        "BLS12_G1ADD": "0x000000000000000000000000000000000000000b",
        "BLS12_G1MSM": "0x000000000000000000000000000000000000000c",
        "BLS12_G2ADD": "0x000000000000000000000000000000000000000d",
        "BLS12_G2MSM": "0x000000000000000000000000000000000000000e",
        "BLS12_PAIRING_CHECK": "0x000000000000000000000000000000000000000f",
        "BLS12_MAP_FP_TO_G1": "0x0000000000000000000000000000000000000010",
        "BLS12_MAP_FP2_TO_G2": "0x0000000000000000000000000000000000000011",
        "P256VERIFY": "0x0000000000000000000000000000000000000100"
      },
      "systemContracts": {
        "BEACON_ROOTS_ADDRESS": "0x000f3df6d732807ef1319fb7b8bb8522d0beac02",
        "CONSOLIDATION_REQUEST_PREDEPLOY_ADDRESS": "0x0000bbddc7ce488642fb579f8b00f3a590007251",
        "DEPOSIT_CONTRACT_ADDRESS": "0x00000000219ab540356cbb839cbe05303d7705fa",
        "HISTORY_STORAGE_ADDRESS": "0x0000f90827f1c53a10cb7a02335b175320002935",
        "WITHDRAWAL_REQUEST_PREDEPLOY_ADDRESS": "0x00000961ef480eb55e80d19ad83579a64c007002"
      }
    },
    "next": {
      "activationTime": 1758004320,
      "blobSchedule": {
        "baseFeeUpdateFraction": 26707819,
        "max": 48,
        "target": 32
      },
      "chainId": "0x1a6bdadc0",
      "forkId": "0xbc00921b",
      "precompiles": {
        "ECREC": "0x0000000000000000000000000000000000000001",
        "SHA256": "0x0000000000000000000000000000000000000002",
        "RIPEMD160": "0x0000000000000000000000000000000000000003",
        "ID": "0x0000000000000000000000000000000000000004",
        "MODEXP": "0x0000000000000000000000000000000000000005",
        "BN254_ADD": "0x0000000000000000000000000000000000000006",
        "BN254_MUL": "0x0000000000000000000000000000000000000007",
        "BN254_PAIRING": "0x0000000000000000000000000000000000000008",
        "BLAKE2F": "0x0000000000000000000000000000000000000009",
        "KZG_POINT_EVALUATION": "0x000000000000000000000000000000000000000a",
        "BLS12_G1ADD": "0x000000000000000000000000000000000000000b",
        "BLS12_G1MSM": "0x000000000000000000000000000000000000000c",
        "BLS12_G2ADD": "0x000000000000000000000000000000000000000d",
        "BLS12_G2MSM": "0x000000000000000000000000000000000000000e",
        "BLS12_PAIRING_CHECK": "0x000000000000000000000000000000000000000f",
        "BLS12_MAP_FP_TO_G1": "0x0000000000000000000000000000000000000010",
        "BLS12_MAP_FP2_TO_G2": "0x0000000000000000000000000000000000000011",
        "P256VERIFY": "0x0000000000000000000000000000000000000100"
      },
      "systemContracts": {
        "BEACON_ROOTS_ADDRESS": "0x000f3df6d732807ef1319fb7b8bb8522d0beac02",
        "CONSOLIDATION_REQUEST_PREDEPLOY_ADDRESS": "0x0000bbddc7ce488642fb579f8b00f3a590007251",
        "DEPOSIT_CONTRACT_ADDRESS": "0x00000000219ab540356cbb839cbe05303d7705fa",
        "HISTORY_STORAGE_ADDRESS": "0x0000f90827f1c53a10cb7a02335b175320002935",
        "WITHDRAWAL_REQUEST_PREDEPLOY_ADDRESS": "0x00000961ef480eb55e80d19ad83579a64c007002"
      }
    },
    "last": {
      "activationTime": 1758102624,
      "blobSchedule": {
        "baseFeeUpdateFraction": 40061729,
        "max": 72,
        "target": 48
      },
      "chainId": "0x1a6bdadc0",
      "forkId": "0x99648079",
      "precompiles": {
        "ECREC": "0x0000000000000000000000000000000000000001",
        "SHA256": "0x0000000000000000000000000000000000000002",
        "RIPEMD160": "0x0000000000000000000000000000000000000003",
        "ID": "0x0000000000000000000000000000000000000004",
        "MODEXP": "0x0000000000000000000000000000000000000005",
        "BN254_ADD": "0x0000000000000000000000000000000000000006",
        "BN254_MUL": "0x0000000000000000000000000000000000000007",
        "BN254_PAIRING": "0x0000000000000000000000000000000000000008",
        "BLAKE2F": "0x0000000000000000000000000000000000000009",
        "KZG_POINT_EVALUATION": "0x000000000000000000000000000000000000000a",
        "BLS12_G1ADD": "0x000000000000000000000000000000000000000b",
        "BLS12_G1MSM": "0x000000000000000000000000000000000000000c",
        "BLS12_G2ADD": "0x000000000000000000000000000000000000000d",
        "BLS12_G2MSM": "0x000000000000000000000000000000000000000e",
        "BLS12_PAIRING_CHECK": "0x000000000000000000000000000000000000000f",
        "BLS12_MAP_FP_TO_G1": "0x0000000000000000000000000000000000000010",
        "BLS12_MAP_FP2_TO_G2": "0x0000000000000000000000000000000000000011",
        "P256VERIFY": "0x0000000000000000000000000000000000000100"
      },
      "systemContracts": {
        "BEACON_ROOTS_ADDRESS": "0x000f3df6d732807ef1319fb7b8bb8522d0beac02",
        "CONSOLIDATION_REQUEST_PREDEPLOY_ADDRESS": "0x0000bbddc7ce488642fb579f8b00f3a590007251",
        "DEPOSIT_CONTRACT_ADDRESS": "0x00000000219ab540356cbb839cbe05303d7705fa",
        "HISTORY_STORAGE_ADDRESS": "0x0000f90827f1c53a10cb7a02335b175320002935",
        "WITHDRAWAL_REQUEST_PREDEPLOY_ADDRESS": "0x00000961ef480eb55e80d19ad83579a64c007002"
      }
    }
  },
  "id": 1
}

```

That's a lot of information clients need to have consensus about!

## How do we ensure that clients use the correct configuration?

To summarize, we have different tests for ensuring this. While we also have ways to verify `eth_config` responses of any locally running execution client (does not require a live devnet), this will not be the focus of the post. In regard to live devnet testing, we make use of multiple approaches:
<br/>
One test we wrote requires prior knowledge: It takes the genesis config used for the devnet in question as input, requests the `eth_config` from each running execution client, and then ensures that the responses are in accordance with the provided configuration file. A brief guide for how to run this test can be found [in our documentation](https://eest.ethereum.org/main/running_tests/execute/eth_config/).
<br/>
Recently, we have added an additional testing mode, the so-called majority mode, which does not require any prior knowledge: this testing mode requests the `eth_config` from each execution client that exists in a given devnet and only compares the hashes of received responses. If any response does not follow the majority response, the test will dump response details, which allows us to notify the affected client teams about their misconfiguration.

![The Office meme for eth_config majority testing](../assets/images/blog/2025-09-15_eth-config/majority_mode.png){ style="display: block; margin: 0 auto; width: 50%;" }

<p style="text-align: center; font-size: 0.9em; color: gray; margin-top: -0.5em;">
We want to ensure that each client uses the exact same configuration.
</p>

Our testing framework makes it very easy for us to specify which clients to compare, what devnet we are testing, etc. The mentioned tests were already successfully used to ensure that clients running in fusaka-devnet-5 are correctly configured in regard to their `eth_config` response. For implementation details refer to [these files](https://github.com/ethereum/execution-spec-tests/tree/98848dfe06ffe9f6faa35f6c5d8d8108d372679e/src/pytest_plugins/execute/eth_config).
<br/>

## TL;DR

Generally, if anything goes wrong, we do not just fix the problem but also ask ourselves how to prevent that thing from happening again. The Holešky incident has shown us that we need a better way of testing client configurations; thus, the work on EIP-7910 began (credits go to Danno Ferrin for championing it), and we have stepped up our testing game by adding additional tests to our framework. In fact, even before a devnet goes live, we try to locally test candidate client builds and collaborate with affected teams in situations where we suspect that misconfiguration might have occurred.

<div style="display:flex; justify-content:space-around; align-items:center;">
  <span style="font-size:40px;">STEEL</span>
  <span style="font-size:160px;">🤝</span>
  <span style="font-size:40px;">Client Teams</span>
</div>
