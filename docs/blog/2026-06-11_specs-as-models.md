---
title: "Specs as Models: Applying Category-Partition Testing to Ethereum's Consensus Layer"
date: 2026-06-11
author: Leo Lara
description: "Reading the executable consensus specs as a formal model to systematically enumerate test scenarios — and the new tests and spec bug it found."
---

<div class="blog-metadata" markdown>
:material-account: [Leo](../team.md#leo-lara) · :material-calendar: June 11, 2026 · :material-clock-outline: 35 min read
</div>

## Summary

We started by researching how tests are generated from specifications in safety-critical industries — avionics, rail signaling, and nuclear control. In these fields, teams write a formal mathematical model of the system and derive tests from its structure, so every meaningful input class is covered by construction rather than by intuition. The core techniques are equivalence partitioning and boundary value analysis: Dick and Faivre (1993) showed how to decompose a specification into Disjunctive Normal Form, where each branch defines one equivalence class; Ostrand and Balcer (1988) gave the practical category-partition framework; and Gaudel (1995) provided the hypotheses that make finite test suites sound.

The limitation in those industries is that the formal model must be written and maintained separately from the code. For Ethereum, that cost is already paid: the consensus specs are executable Python that *is* the authoritative specification. So these specification-side techniques can be applied directly to the code, with no separate model.

Ethereum's consensus layer runs on five independent clients — Prysm, Lighthouse, Teku, Lodestar, and Nimbus. They must all produce the same output for every input. Any disagreement, even on one edge case, can split the chain. A shared test suite prevents this. The [`ethereum/consensus-specs`](https://github.com/ethereum/consensus-specs) repository holds executable Python functions that define the state transition rules, plus test vectors that every client must pass.

Domain experts write the current test suite, and it covers the protocol well. But it cannot answer one question: for a given spec function, how many distinct input scenarios exist, and how many are actually tested? Take `process_proposer_slashing`. It runs a sequential pipeline of six validation checks, plus fork-specific logic for builder payments. A systematic enumeration of its input space finds 25 distinct scenarios. The existing suite had 18 tests, written across several forks, and they covered 18 of those scenarios — 72% scenario coverage. (Scenario coverage is the fraction of equivalence classes that at least one test exercises.) The other 7 scenarios were untested, including one — headers with different slots in the same epoch — that hit a validation path no test had ever reached.

These gaps are not bad work. Expert judgment picks representative cases, but it cannot guarantee complete enumeration without a reference list of all distinct scenarios. This post describes a two-step method that builds such a list. Step 1 documents the input and output space of the function. Step 2 applies equivalence partitioning to derive every meaningful scenario and maps existing tests against them. The method treats the Python specs as what they already are: a formal model written in executable code. Each `assert` defines a partition boundary, each `if` branch defines a dimension of variation, and each inlined helper adds sub-conditions. The information needed to enumerate the test scenarios is already in the spec.

The method has been applied to three functions:

- For `process_proposer_slashing`, it produced 20 new tests — 6 scenario gap-fillers and 14 boundary value tests — in [PR #4871](https://github.com/ethereum/consensus-specs/pull/4871), raising scenario coverage from 72% to 96%.
- For `process_withdrawals`, the analysis found a defect in `update_next_withdrawal_validator_index`, which did not handle the `BUILDER_INDEX_FLAG` added in the Gloas fork. The bug is in [PR #4835](https://github.com/ethereum/consensus-specs/pull/4835), with tests in [PR #4830](https://github.com/ethereum/consensus-specs/pull/4830).
- For `process_deposit_request`, which uses routing logic instead of sequential validation, the same analysis found 23 scenarios with 17 covered and 6 gaps — 74% scenario coverage — addressed in [PR #4906](https://github.com/ethereum/consensus-specs/pull/4906).

The rest of this post describes the method, the results for each function, and how it can scale with AI to cover the dozens of spec functions changed in every hard fork.

## The Testing Landscape and the Gap This Method Addresses

Many techniques generate tests. Most belong to two families: techniques that work *from the code* and techniques that work *from a specification*. The consensus specs allow both families, but neither has been used to systematically enumerate input scenarios.

### Working from the code

The most common approach is code coverage: generate tests until a metric — line, branch, or MC/DC coverage — reaches a target. Clients do this: Lighthouse tracks Rust coverage, Prysm tracks Go coverage. The problem is that coverage of the *implementation* does not tell you whether every meaningful *spec scenario* is tested. A Rust client can reach 100% branch coverage of its `process_proposer_slashing` and still never exercise the "slots differ within the same epoch" scenario, because nothing in the implementation forces that distinction. The implementation may handle this case the same as cross-epoch slot differences — which is the problem. If a later refactor changes that handling, no test catches the regression.

Fuzzing works differently: it generates random or mutated inputs, sends them to several clients, and compares outputs. Ethereum has active differential fuzzing — for example Sigma Prime's [beacon-fuzz](https://github.com/sigp/beacon-fuzz), built for the Ethereum Foundation — which runs inputs across clients to find disagreements. Fuzzing is good at finding crashes and divergences, but it cannot guarantee completeness. A fuzzer can run for months and never generate the exact combination of validator states, epoch timing, and header content that triggers a subtle edge case. And there is no way to look at a fuzzing campaign and list the scenarios it has not yet hit. No detected failure is not the same as full coverage.

Symbolic execution replaces concrete inputs with symbolic variables and uses an SMT solver to explore all paths. In theory it is the most powerful code-based technique. Tools like [CrossHair](https://github.com/pschanely/CrossHair) apply it to Python. For functions without loops it works well: it produced exactly 4 test cases for `is_slashable_validator`, covering all branch combinations. But consensus-spec functions often loop over validator sets, and there symbolic execution has a problem. For `process_attester_slashing`, which iterates over validator indices, CrossHair generated 42 concrete test cases — one per combination of list length and element position it explored. The same function has 7 meaningful equivalence classes ("all validators slashable", "none slashable", "mixed", and so on). The 42 cases are all instances of those 7 classes, but the tool cannot show this. It returns a flat list of inputs with no semantic grouping and no sign of which scenarios are still uncovered.

Property-based testing (for example [Hypothesis](https://hypothesis.readthedocs.io/)) defines invariants that should always hold, then generates random inputs that meet the preconditions and checks the invariants. This is useful for finding violations, but it answers a different question. It verifies that properties hold across random samples, not that every distinct scenario was exercised. Passing one million property-based tests does not guarantee all equivalence classes were tested.

All these techniques share one trait: they work from the code outward, trying to exercise it. None answers the question: how many distinct input scenarios does this function have, and which ones are not covered?

### Working from a specification

The formal methods community has long derived tests from specifications. The idea is simple: given a mathematical model of the system, you can analyze its structure to find exactly which input classes exist and generate tests for each one.

Model-based testing starts from a formal specification written in a language such as TLA+, B Method, VDM, or Dafny, and uses tools to generate test cases that cover the model's state space. It is well-established in safety-critical fields like avionics, rail signaling, and nuclear control. For Ethereum, ConsenSys built [`eth2.0-dafny`](https://github.com/ConsenSys/eth2.0-dafny), a Dafny formalization of Phase 0. It was a large effort, but it required writing and maintaining a *separate* formal model next to the Python spec. Few teams have the resources for this, and such models tend to fall behind the spec as hard forks change dozens of functions.

Equivalence partitioning and boundary value analysis — the techniques at the center of this method — also come from formal methods. The foundational work is Dick and Faivre's 1993 paper "Automating the Generation and Sequencing of Test Cases from Model-Based Specifications," which showed how to decompose a VDM specification into Disjunctive Normal Form, where each disjunct defines one equivalence class. Ostrand and Balcer's Category-Partition Method (1988) gives the practical framework for identifying input dimensions and their classes. Boundary value analysis (Jorgensen) adds testing at the edges of each class — the ON/IN/OUT points where off-by-one errors happen. The "Theoretical foundations" section below presents these formally.

These specification-side techniques work because they derive tests from the *spec's structure*, so they cover meaningful scenarios by construction. Their historical limit: they need a formal specification in a declarative notation — VDM, Z, B — separate from the executable code. They have not been applied systematically to executable Python.

### Executable specs as a bridge between both approaches

The Ethereum consensus specs are in a special position. They are not an implementation with tests added on top. They are not a formal specification in a declarative language. They are executable Python code that *is* the authoritative specification. Every client must reproduce these Python functions exactly. So specification-side techniques — partition analysis, boundary values, scenario enumeration — can be applied directly to the code, with no separate formal model.

Every `assert` defines a partition boundary: inputs that satisfy it and inputs that do not. Every `if` branch defines a dimension of variation. Every `for` loop over a collection produces iteration-behavior classes: zero iterations, all elements on one path, some elements on different paths. Every inlined helper (for example, `is_slashable_validator` inside `process_proposer_slashing`) adds sub-condition dimensions that multiply the scenario space. All this is explicit in the code.

What Dick and Faivre did with VDM predicates can be done with Python `assert` statements and `if` branches. The result is a hybrid that does not fit cleanly in either family: **specification-based structural testing** — using the spec's own code structure to derive a provably complete enumeration of test scenarios. This is what enables the two-step technique.

## Reading the Spec as a Testable Model

Actual spec code shows the partition structure directly. The "Theoretical foundations" section below gives the formal definitions of equivalence partitions, Disjunctive Normal Form, and the related concepts used here.

The following is the core of `process_proposer_slashing` from the Gloas fork, reduced to its essential structure:

```python
def process_proposer_slashing(state: BeaconState, proposer_slashing: ProposerSlashing) -> None:
    header_1 = proposer_slashing.signed_header_1.message
    header_2 = proposer_slashing.signed_header_2.message

    # Validation pipeline — each assert is a partition boundary
    assert header_1.slot == header_2.slot                          # (1)
    assert header_1.proposer_index == header_2.proposer_index      # (2)
    assert header_1 != header_2                                    # (3)
    proposer = state.validators[header_1.proposer_index]
    assert is_slashable_validator(proposer, get_current_epoch(state))  # (4)
    # ... BLS signature verification for both headers ...          # (5, 6)

    # Fork-specific logic — each branch is a dimension
    proposal_epoch = compute_epoch_at_slot(header_1.slot)
    if proposal_epoch == get_current_epoch(state):                 # (7a)
        state.builder_pending_payments[...] = BuilderPendingPayment()
    elif proposal_epoch == get_previous_epoch(state):              # (7b)
        state.builder_pending_payments[...] = BuilderPendingPayment()
    # else: older epoch, no payment deletion                       # (7c)

    slash_validator(state, header_1.proposer_index)
```

Every line tells us something about the test space. The six `assert` statements form a sequential validation pipeline: each one passes (execution continues) or fails (raises `AssertionError`). In Dick and Faivre's terms, each `assert` creates a binary partition — inputs that satisfy the condition and inputs that do not. Because the asserts are sequential, a failure on assert (1) means asserts (2) through (6) are never reached. So the partitions are *ordered*: to test a failure on assert (3), the inputs must satisfy asserts (1) and (2). The set of all entry-to-exit paths through this pipeline is the Disjunctive Normal Form of the function's input space.

Assert (4) is special because it calls a helper, `is_slashable_validator`, which has three sub-conditions: the validator must not be already slashed, must be active (activation epoch ≤ current epoch), and must not yet be withdrawable (current epoch < withdrawable epoch). When inlined, a single assert becomes three independent partition dimensions. The [spec-doc for this function](https://notes.ethereum.org/@leolara/test_process_proposer_slashing) lists all six validation conditions, including these sub-conditions, which makes the full partition structure visible.

The `if/elif/else` block at the bottom adds a different kind of dimension. It only matters when all six checks pass — it is a dimension of the *valid path*, not a failure mode. It splits the valid slashing scenarios into three timing classes: current epoch, previous epoch, and older. Each produces different behavior — payment deletion or no payment deletion — so each needs its own test.

Now a function with a different structure. `process_deposit_request` in the Gloas fork routes deposits based on two lookups and a credential prefix:

```python
is_builder = deposit_request.pubkey in builder_pubkeys
is_validator = deposit_request.pubkey in validator_pubkeys
is_builder_prefix = is_builder_withdrawal_credential(deposit_request.withdrawal_credentials)

if is_builder or (is_builder_prefix and not is_validator):
    apply_deposit_for_builder(...)
    return

state.pending_deposits.append(PendingDeposit(...))
```

This is not a validation pipeline; it is routing logic. The partition structure comes from three boolean dimensions: is the pubkey an existing builder, is it an existing validator, and does the credential have the builder prefix (`0x03`). The cross-product is eight combinations, but the routing condition collapses some. An existing builder always takes the builder path, whatever the credentials. A new pubkey with builder credentials and no validator match also takes the builder path. All other cases queue a validator deposit. The analysis maps each of the eight combinations to its routing outcome and checks which ones have tests.

Different spec functions have different structures — sequential validation, routing logic, multi-phase pipelines with loops — but each structure has a systematic reading that produces its partition dimensions. The `assert` statements, `if` branches, `for` loops, and inlined helpers all have well-defined partition semantics. You do not invent a model. You read the code with one question in mind: what are the independent dimensions of variation in this function's input space, and what classes does each dimension contain?

This is what the two-step technique formalizes.

## The Method: Two-Step Input-Space Analysis

The method has two steps, each producing a defined artifact. Step 1 documents the territory: every field the function reads, writes, and checks, and every helper it calls. Step 2 partitions that territory: it finds the independent dimensions of variation, lists the classes in each, and maps existing tests against the combination matrix. The gap between the tests that exist and the tests that should exist is the output.

### Step 1: Input/Output Space Documentation (the "spec-doc")

Before partitioning the input space, you need to know what it *is*. For a consensus-spec function, this means answering six questions: which fields does it read? Which does it modify? Which conditions does it assert? Which helpers does it call, and which fields do *they* access? Which numeric constants and thresholds matter? And which tests already exist?

The output is a structured document — the "spec-doc" — in a standard format. For `process_proposer_slashing`, the [spec-doc](https://notes.ethereum.org/@leolara/test_process_proposer_slashing) starts with the input fields table. This is not just a list of parameter types. It maps every state field the function touches, with its type, value range, cross-field constraints, and purpose:

| Field | Type | Constraints | Purpose |
|-------|------|-------------|---------|
| `header_1.slot` | `Slot (uint64)` | Must equal `header_2.slot` | Slot of the block header |
| `header_1.proposer_index` | `ValidatorIndex` | Must equal `header_2.proposer_index`; must be < `len(validators)` | Index into validator registry |
| `proposer.slashed` | `bool` | Must be `False` for slashability | Whether validator already slashed |
| `proposer.activation_epoch` | `Epoch` | Must be ≤ `current_epoch` | When validator became active |
| `proposer.withdrawable_epoch` | `Epoch` | Must be > `current_epoch` | When validator can withdraw |
| `builder_pending_payments` | `Container[64]` | Indexed by slot within 2-epoch window | Gloas builder payment state |

The spec-doc then lists the six validation conditions (shown in "Reading the Spec as a Testable Model"), the call tree — noting that `is_slashable_validator` inlines three sub-conditions and that `slash_validator` chains through `initiate_validator_exit` and balance updates — and the key constants (`SLOTS_PER_EPOCH = 32`, `FAR_FUTURE_EPOCH = 2^64 - 1`, and so on).

The spec-doc also inventories the existing tests. For `process_proposer_slashing`, this was 15 tests inherited from Phase 0 (the basic valid case, each individual validation failure, and signature edge cases), plus 3 Gloas-specific tests for builder payment deletion — 18 in total. This inventory is the baseline for the coverage audit in Step 2.

The spec-doc is the "map of the territory." It makes no testing decisions. It just describes what the function does, structurally and in full. When Step 1 is done well, Step 2 becomes almost mechanical.

### Step 2: Equivalence Partition Analysis (the "eq-partition")

Step 2 takes the spec-doc as input and produces a partition analysis: a set of dimensions, each with classes, boundary values, test mappings, and gap identification.

The procedure is the same for each validation condition or branch in the spec-doc. First, find the *dimension* — the independent aspect of the input being tested. Second, list the *classes* — the distinct values or categories that produce different behavior. For numeric comparisons, find the *boundary values* — the ON point (exact boundary), the IN point (just inside the valid region), and the OUT point (just outside it). Finally, check which classes and boundaries existing tests cover, and flag the gaps.

For `process_proposer_slashing`, the [eq-partition](https://notes.ethereum.org/@leolara/eq-partition-proposer-slashing) found 13 dimensions (P1 through P13). Here is one, P9 — Validator Withdrawable Status — which shows the level of detail:

| Class | Condition | Valid? |
|-------|-----------|--------|
| P9.1: Not withdrawable | `withdrawable_epoch > current_epoch` | Valid |
| P9.2: Already withdrawable | `withdrawable_epoch ≤ current_epoch` | Invalid |

The boundary values are:

| Boundary | Condition | Description |
|----------|-----------|-------------|
| P9.1B1 | `withdrawable_epoch == current_epoch + 1` | Minimum valid (withdrawable next epoch) |
| P9.1B2 | `withdrawable_epoch == FAR_FUTURE_EPOCH` | Sentinel value (never set) |
| P9.2B1 | `withdrawable_epoch == current_epoch` | Minimum invalid (just became withdrawable) |

The coverage mapping: P9.1 is covered by `test_basic` (implicitly, via the `FAR_FUTURE_EPOCH` default). P9.2 is covered by `test_invalid_proposer_is_withdrawn`. But boundary P9.1B1 — a validator withdrawable in the *next epoch* (the minimum valid case) — has no test. This is a gap.

After analyzing each of the 13 dimensions, the eq-partition combines them into a cross-product coverage table. Not all combinations are meaningful: the Gloas builder payment dimensions (P12, P13) apply only when all core checks pass, and compound failures (several invalid dimensions at once) are low priority because they fail on the first check. The table reduces to 25 meaningful combinations, each mapped to an existing test or marked as uncovered.

The final scenario-coverage statistics for `process_proposer_slashing`:

| Category | Total | Covered | Gaps |
|----------|-------|---------|------|
| Valid slashing combinations | 6 | 3 | 3 |
| Single invalid partition | 13 | 12 | 1 |
| GLOAS combinations | 6 | 3 | 3 |
| **Total** | **25** | **18** | **7** |

That is 72% scenario coverage. There are seven gaps, each with a description of the untested scenario and a suggested test name: `test_block_header_from_past`, `test_self_slashing_future_slot`, `test_invalid_slots_same_epoch_different_slot`, among others.

### Theoretical foundations

The two-step technique combines three established ideas from the testing and formal methods literature: equivalence partitioning, boundary value analysis, and converting program predicates to Disjunctive Normal Form. This subsection gives the formal background that the earlier sections referenced informally.

**Equivalence classes and the input partition.** Let `f : I → O` be a function from input domain `I` to output domain `O`. An equivalence relation `~` on `I` (reflexive, symmetric, transitive) induces a partition `I/~ = { [x] : x ∈ I }`, where `[x] = { y ∈ I : x ~ y }` is the equivalence class of `x`. The relation that matters for testing groups inputs that produce equivalent observable behavior in `f`. Equivalence partitioning, introduced by Myers (1979), partitions `I` into such classes and selects one representative from each. The justification is the *uniformity hypothesis* (Gaudel, 1995): if `f` is correct on one input from a class, it is correct on all inputs from that class. Equivalence partitioning is sound only when this hypothesis holds for the chosen partition.

**Partition algebra.** When several aspects of the input vary independently, each defines its own partition of `I`. Given two partitions `P_1, P_2` of the same set, their *meet* `P_1 ∧ P_2` (the greatest common refinement) has classes `{ B_1 ∩ B_2 : B_1 ∈ P_1, B_2 ∈ P_2, B_1 ∩ B_2 ≠ ∅ }`. The set of all partitions of `I` forms a lattice under refinement: `P_1 ≤ P_2` if every class of `P_1` sits inside a class of `P_2`. For partitions on different sets `A` and `B`, the *product partition* on `A × B` has classes `B_i × C_j`. The combined partition from Step 2 is the meet of the per-dimension partitions, restricted to the feasible combinations. The lattice formalism is background; in the testing literature, Ostrand and Balcer's Category-Partition Method (1988) uses the cross-product directly, with constraints to remove infeasible combinations, but does not name the lattice structure.

**Predicate structure and Disjunctive Normal Form.** A formula is in *Disjunctive Normal Form* (DNF) if it is a disjunction of conjunctions of literals: `D = C_1 ∨ C_2 ∨ ... ∨ C_n`, where each `C_i = l_{i,1} ∧ l_{i,2} ∧ ...` and each literal `l_{i,j}` is an atomic predicate or its negation. Every Boolean formula has a DNF; the conversion follows from the truth table. Dick and Faivre (1993) used DNF for systematic test generation from VDM specifications: given an operation with predicates `p_1, ..., p_k` (from preconditions, postconditions, and inlined helper conditions), the conjoined predicate is reduced to DNF, each disjunct `C_i` defines one equivalence class, and one input is selected from each `{ x ∈ I : C_i(x) }`. Two limits apply. First, the DNF expansion can produce up to `2^k` disjuncts, many infeasible (their conjunction is unsatisfiable), so a constraint analysis is needed to remove them. Second, the completeness claim is *relative to the predicates considered*: every behavioral class induced by `p_1, ..., p_k` is covered, but a missing predicate is invisible to the method.

**Sequential validation pipelines.** A common structure in the consensus specs is a chain of asserts:

```
assert A_1
assert A_2
...
assert A_n
```

The function exits successfully if all asserts pass, and raises `AssertionError` at the first failing one. The reachable behavior is described by `n + 1` disjuncts:

- `A_1 ∧ A_2 ∧ ... ∧ A_n` — all asserts pass; the function completes.
- `¬A_1` — fails immediately at assert 1.
- `A_1 ∧ ¬A_2` — fails at assert 2 after assert 1 passes.
- ...
- `A_1 ∧ ... ∧ A_{n-1} ∧ ¬A_n` — fails at the last assert.

These `n + 1` disjuncts are the DNF of the program's exit semantics, and each one is one entry-to-exit path. A test suite with one input per disjunct gives path coverage of the pipeline; under the uniformity hypothesis, this is a sound and complete test of the sequential structure with respect to the spec. This is a direct corollary of Dick and Faivre (1993) combined with Gaudel (1995); the literature gives it no separate name.

**Boundary values.** The disjuncts above describe *which combinations* of predicate truth values are reachable. They do not describe *which numeric inputs* to select within each combination. Boundary value analysis (Jorgensen) addresses this. For a numeric predicate like `x ≤ c`, the truth value changes at `x = c`. The boundary values are: ON (`x = c`, the exact boundary), IN (just inside the valid region, e.g., `x = c - 1`), and OUT (just outside, e.g., `x = c + 1`). Robust boundary value analysis selects all three. The empirical justification — that off-by-one errors and wrong comparison operators concentrate at boundaries — is widely accepted, though Hamlet and Taylor (1990) showed it is provably better than random testing only when faults are in fact concentrated near boundaries.

**Loops and the regularity hypothesis.** Functions with loops over collections add another dimension: the loop's behavior depends on what the body does across iterations, and the iteration count is in general unbounded. Gaudel's *regularity hypothesis* parameterizes the input by a size measure (loop count, list length) and assumes the program's behavior beyond a chosen size is correctly extrapolated from its behavior at smaller sizes. Combined with the uniformity hypothesis on the per-iteration behavior, this allows finite test suites for unbounded iteration. The "Loop Case" section applies this to `process_attester_slashing`.

**Synthesis.** The two-step method combines these as follows. The spec-doc (Step 1) makes explicit the predicates `p_1, ..., p_k` the function checks: the asserts, the branch conditions, and the sub-conditions hidden in inlined helpers. The eq-partition (Step 2) builds the partition induced by these predicates, finds the reachable disjuncts (the DNF of the exit semantics), maps existing tests to disjuncts, and adds boundary values for each numeric predicate. The novelty is not the theory: Dick and Faivre, Ostrand and Balcer, Jorgensen, and Gaudel all predate this work. The novelty is applying these techniques to executable Python that *is* the protocol specification, and using the spec-doc to translate imperative code into the structured predicate description that the partition theory was designed for.

## End-to-End Application: `process_proposer_slashing`

The previous sections described the technique in the abstract. This section applies it end-to-end to one function: the full dimension landscape, the full coverage table, the specific gaps, and the result of filling them.

### The partition dimensions

The spec-doc for `process_proposer_slashing` (condensed in "The Method") is the input for the [eq-partition analysis](https://notes.ethereum.org/@leolara/eq-partition-proposer-slashing), which found 13 independent dimensions. Each one is an aspect of the input that the function distinguishes through its validation logic, branching, or inlined helper conditions.

The first group comes from the sequential validation pipeline — the six `assert` statements at the top. Each assert produces at least one dimension:

**P1 — Header Slot Relationship** has three classes: slots equal (valid), slots different within the same epoch (invalid), and slots in different epochs (invalid). The two invalid classes fail the same `header_1.slot == header_2.slot` check, but they are distinct equivalence classes — same-epoch slot differences have different implications from cross-epoch ones.

**P2 — Proposer Index** has three classes: indices equal and valid, indices different, and index out of bounds (≥ `len(validators)`).

**P3 — Header Content Distinction** has three classes: headers differ in at least one root field, headers identical with the same signatures, and headers identical with different signatures. The two identical-header classes both fail `header_1 != header_2`, but through different input configurations.

**P4, P5 — Individual Signature Validity** are binary (valid/invalid) for each header's BLS signature. **P6 — Combined Signature States** is the cross-product: both valid, both invalid, only signature 1 invalid, only signature 2 invalid, and signatures swapped between headers. This compound dimension matters because the sequential check order means "signature 1 invalid" fails at a different point from "signature 2 invalid."

**P7, P8, P9 — Slashability Sub-Conditions** come from inlining `is_slashable_validator`. Each is binary: activated or not (P7), already slashed or not (P8), already withdrawable or not (P9). These are the three sub-conditions behind a single `assert`.

The second group covers valid-path variations — dimensions relevant only when all checks pass:

**P10 — Slasher Identity**: the block proposer is a different validator (the standard case) versus the block proposer slashes itself (the whistleblower is the slashed proposer). Both are valid, but they produce different balance effects.

**P11 — Header Slot Timing**: the header slot is in the past, at the current slot, or in the future relative to `state.slot`. All three are valid (the spec allows future-slot headers), but each exercises a different state context.

The third group is fork-specific:

**P12 — Builder Payment Deletion Timing** (Gloas only): the proposal epoch is current, previous, or older. The first two trigger payment deletion; the third does not.

**P13 — Builder Payment State** (Gloas only): the payment slot has an existing payment or is already empty. Deleting an existing payment and deleting an empty slot are behaviorally distinct.

These dimensions are **hierarchical**. P12 and P13 apply only when P1 through P9 are all in their valid class — builder payment logic is never reached if any check fails. Likewise, P10 and P11 are meaningful only on the valid path. This hierarchy determines which cross-product combinations are meaningful.

### The coverage table

The full cross-product is very large, but the hierarchy and infeasibility constraints reduce it to 25 meaningful combinations plus 8 low-priority compound failures. Each meaningful combination is one distinct test scenario.

Here is the condensed coverage table, each row mapped to an existing test or marked as a gap:

| # | Scenario | Covered | Test |
|---|----------|---------|------|
| 1 | Valid + past slot + different slasher | **Gap** | — |
| 2 | Valid + current slot + different slasher | ✓ | `test_basic` |
| 3 | Valid + future slot + different slasher | ✓ | `test_block_header_from_future` |
| 4 | Valid + past slot + self-slashing | **Gap** | — |
| 5 | Valid + current slot + self-slashing | ✓ | `test_slashed_and_proposer_index_the_same` |
| 6 | Valid + future slot + self-slashing | **Gap** | — |
| 7 | Invalid: slots differ, same epoch | **Gap** | — |
| 8 | Invalid: slots differ, different epochs | ✓ | `test_invalid_slots_of_different_epochs` |
| 9 | Invalid: different proposer indices | ✓ | `test_invalid_different_proposer_indices` |
| 10 | Invalid: proposer index out of bounds | ✓ | `test_invalid_incorrect_proposer_index` |
| 11 | Invalid: identical headers, same sigs | ✓ | `test_invalid_headers_are_same_sigs_are_same` |
| 12 | Invalid: identical headers, diff sigs | ✓ | `test_invalid_headers_are_same_sigs_are_different` |
| 13 | Invalid: signature 1 invalid | ✓ | `test_invalid_incorrect_sig_1` |
| 14 | Invalid: signature 2 invalid | ✓ | `test_invalid_incorrect_sig_2` |
| 15 | Invalid: both signatures invalid | ✓ | `test_invalid_incorrect_sig_1_and_2` |
| 16 | Invalid: signatures swapped | ✓ | `test_invalid_incorrect_sig_1_and_2_swap` |
| 17 | Invalid: proposer not activated | ✓ | `test_invalid_proposer_is_not_activated` |
| 18 | Invalid: proposer already slashed | ✓ | `test_invalid_proposer_is_slashed` |
| 19 | Invalid: proposer already withdrawn | ✓ | `test_invalid_proposer_is_withdrawn` |
| 20 | GLOAS: current epoch + payment exists | ✓ | `test_builder_payment_deletion_current_epoch` |
| 21 | GLOAS: current epoch + payment empty | **Gap** | — |
| 22 | GLOAS: previous epoch + payment exists | ✓ | `test_builder_payment_deletion_previous_epoch` |
| 23 | GLOAS: previous epoch + payment empty | **Gap** | — |
| 24 | GLOAS: older epoch + payment exists | ✓ | `test_builder_payment_deletion_too_late` |
| 25 | GLOAS: older epoch + payment empty | **Gap** | — |

In total: 18 covered scenarios, 7 gaps, 72% scenario coverage.

### The seven gaps

The gaps fall into three categories. The first is valid-path timing variations: no test exercises a proposer slashing where the header slot is in the past (combinations 1 and 4), and no test exercises self-slashing with a future-slot header (combination 6). These are not unusual — a proposer slashing can reference any past slot where the proposer produced conflicting headers. The existing tests default to current-slot headers because the helper `get_valid_proposer_slashing` uses `slot=state.slot`.

The second category is the same-epoch slot mismatch (combination 7). This is the most relevant gap. The existing test `test_invalid_slots_of_different_epochs` exercises headers with slots in *different* epochs — for example, slot 64 and slot 96. But headers with slots in the *same* epoch — for example, slot 64 and slot 65 — fail the same `header_1.slot == header_2.slot` check while being a distinct equivalence class. An implementation that handles these two cases differently (for example, by optimizing same-epoch slot comparisons) would have a bug that no current test catches.

The third category is the Gloas builder payment empty-slot cases (combinations 21, 23, 25). All existing tests configure a non-empty builder pending payment before slashing and then check it is deleted. No test checks the behavior when the payment slot is *already empty*. The function still writes `BuilderPendingPayment()` to the slot, which should be a no-op; but an implementation that skips the write when the slot is empty would diverge from the spec.

### Boundary conditions: where defects typically occur

The equivalence class gaps show *which scenarios* are missing. Boundary value analysis shows *where within each scenario* bugs are most likely. For every numeric comparison in the partition dimensions, the eq-partition finds the ON point (the exact boundary), the IN point (just inside the valid region), and the OUT point (just outside). These are where off-by-one errors, wrong comparison operators (`<` versus `<=`), and edge-case arithmetic failures happen.

Take the three sub-conditions inside `is_slashable_validator`. The activation check is `activation_epoch <= current_epoch`. The ON boundary is `activation_epoch == current_epoch` — a validator activated in the current epoch, the minimum valid case. The OUT boundary is `activation_epoch == current_epoch + 1` — activates next epoch, the smallest invalid value. The withdrawable check is `current_epoch < withdrawable_epoch`. The ON boundary is `withdrawable_epoch == current_epoch + 1` — withdrawable next epoch, the minimum valid case. The OUT boundary is `withdrawable_epoch == current_epoch` — just became withdrawable, the minimum invalid case.

These are not academic distinctions. A client that implements the activation check as `activation_epoch < current_epoch` (strict less-than instead of less-than-or-equal) would wrongly reject validators activated in the current epoch. This is a consensus-breaking bug, and it shows up only at the exact boundary. The boundary analysis found that `activation_epoch == current_epoch` had no explicit test — the existing tests used validators activated long ago (far inside the valid region) or activating next epoch (on the invalid side). The boundary itself was never tested directly.

The same pattern applies to other dimensions. For header slot relationships (P1), the eq-partition found three boundary values: a slot at the start of an epoch (`slot % SLOTS_PER_EPOCH == 0`), a slot at the end (`slot % SLOTS_PER_EPOCH == 31`), and a future slot relative to `state.slot`. Only the future-slot boundary was tested explicitly (by `test_block_header_from_future`); the epoch-boundary slots were covered only implicitly — the helper picks a slot that may or may not be on an epoch boundary, depending on the test state. For header content distinction (P3), the existing tests differentiated headers only by changing `parent_root` (the field the helper changes by default). No test checked single-field differences in `state_root` or `body_root`, and no test checked multiple root fields differing at once.

The overall boundary coverage:

| Dimension | Boundaries | Explicitly tested | Implicitly covered | Not covered |
|-----------|-----------|-------------------|-------------------|-------------|
| P1: Slot Relationship | 3 | 1 | 2 | 0 |
| P2: Proposer Index | 3 | 1 | 2 | 0 |
| P3: Header Content | 4 | 1 | 0 | 3 |
| P7: Activation Status | 2 | 1 | 0 | 1 |
| P9: Withdrawable Status | 4 | 1 | 2 | 1 |
| P12: Payment Timing | 5 | 1 | 4 | 0 |
| **Total** | **21** | **6** | **10** | **5** |

Only 6 of 21 boundary values were tested explicitly — 29% explicit boundary coverage. Another 10 were covered implicitly (the test reaches the boundary by coincidence, not design). Five boundaries had no coverage. The implicit coverage is fragile: if a helper changes how it generates default values, the accidental boundary coverage is lost without warning.

### From gaps to tests

The seven equivalence class gaps and the boundary coverage gaps together served as the specification for new tests in [PR #4871](https://github.com/ethereum/consensus-specs/pull/4871) ("Add more proposer slashing tests"). The PR added 20 new tests: 6 scenario gap-filling tests (one low-priority gap — self-slashing with a past-slot header — was deferred) and 14 boundary value tests covering epoch-boundary slots, the minimum and maximum valid proposer index, single-field header differences in `state_root` and `body_root`, the activation and withdrawable epoch edge cases, and builder payment timing boundaries. After this PR, scenario coverage went from 72% (18/25) to 96% (24/25).

The partition analysis was the input, the tests were the output. The pipeline — spec-doc to eq-partition to gap identification to test code — moved the process from a subjective assessment ("I think the tests are probably fine") to an explicit list of specific missing scenarios and boundaries, which were then addressed.

## Two Additional Functions: Generalization of the Method

`process_proposer_slashing` is a sequential validation pipeline — maybe the simplest structure a spec function can have. The same two-step technique was applied to two functions with very different structures. Both produced new tests, and one revealed a bug in the spec itself.

### `process_withdrawals`: a multi-phase pipeline

`process_withdrawals` has a very different structure. It has no sequential `assert` statements. Instead it runs a four-phase withdrawal pipeline: first builder pending withdrawals, then partial validator withdrawals, then a builder sweep, and finally a validator sweep. Each phase has its own eligibility logic, its own iteration pattern, and its own cap on the number of withdrawals. The phases share a global budget (`MAX_WITHDRAWALS_PER_PAYLOAD = 16`), with all phases except the validator sweep capped at 15 in total, which reserves at least one slot for the validator sweep.

The function also has an early exit that `process_proposer_slashing` does not: if `is_parent_block_full(state)` returns `False` (the parent block's execution payload bid does not match the latest block hash), the function returns immediately without changing any state.

The Gloas fork changed this function a lot. EIP-7732 (Enshrined Proposer-Builder Separation) introduced builders as separate non-validating staked actors with their own registry, balances, and withdrawal logic. The [spec-doc](https://notes.ethereum.org/@leolara/test_process_withdrawals) needed to map an input space that includes `state.builders[]` with their balances, execution addresses, and withdrawable epochs; `state.builder_pending_withdrawals[]` with builder indices, fee recipients, and amounts; plus the existing validator fields from Electra. The output space includes changes to builder balances, validator balances, pending withdrawal lists (sliced to remove processed items), sweep indices, and the `payload_expected_withdrawals` list given to the execution layer.

The partition dimensions here differ from those of `process_proposer_slashing`. Instead of "does this assert pass or fail", the dimensions are questions like: does the builder pending withdrawal list have items? Is the requested amount greater or less than the builder's balance? Does the builder sweep index wrap around the registry? Are partial withdrawals controlled by `withdrawable_epoch`? How do the phases interact when the global budget is nearly exhausted — can builder pending withdrawals starve the validator sweep of slots?

The spec-doc went with the test file in [PR #4830](https://github.com/ethereum/consensus-specs/pull/4830) as `test_process_withdrawals.md` — a 232-line document mapping the full input/output space. The reviewer could see exactly which part of the input space the tests covered, and the reasoning behind that coverage.

The most important result was not a test gap but a spec bug. While documenting how `process_withdrawals` calls `update_next_withdrawal_validator_index` (a function inherited from Capella), the analysis found that this function reads a `ValidatorIndex` that, since the Gloas fork, could hold a `BUILDER_INDEX_FLAG`. The Capella-era function did not handle this flag — it would read a builder-flagged index as a validator index, referencing a validator that does not exist. This is in [PR #4835](https://github.com/ethereum/consensus-specs/pull/4835) ("[DO NOT MERGE] Bug in Gloas specs due to BUILDER_INDEX_FLAG"). The bug was real, no other review process had caught it, and it was fixed in a separate PR. The systematic input-space analysis found a defect in the spec itself, not only a missing test.

The tests from the analysis are in [PR #4830](https://github.com/ethereum/consensus-specs/pull/4830).

### `process_deposit_request`: routing logic

The third function, `process_deposit_request`, has yet another structure. The [spec-doc](https://notes.ethereum.org/@leolara/test_process_deposit_request) shows it is neither a sequential validation pipeline nor a multi-phase pipeline. It is a router: deposits arrive with a pubkey and withdrawal credentials, and the function decides whether to route them to the builder path (applied immediately) or the validator path (queued in `pending_deposits`).

The routing decision depends on the cross-product of three conditions: whether the pubkey matches an existing builder, whether it matches an existing validator, and whether the withdrawal credentials have the builder prefix (`0x03`). An existing builder always takes the builder path, whatever the credentials. An existing validator always takes the validator path, even with builder credentials. A new pubkey takes the builder path if it has builder credentials, and the validator path otherwise. The [eq-partition](https://notes.ethereum.org/@leolara/eq-partition-process_deposit_request) maps each routing combination and checks which ones have tests.

The analysis goes beyond routing. For the builder path there is a sub-dimension: whether the builder deposit is a top-up (an existing builder whose balance is incremented) or a new builder creation. For a new builder creation, the signature must be valid — a condition not checked for top-ups or validator deposits. And for a new builder creation, there is another dimension: whether there is a reusable slot in the builder registry (a builder whose `withdrawable_epoch <= current_epoch` and whose balance is zero), or whether the new builder is appended to the end of the registry.

The boundary analysis for this function is extensive. The deposit amount dimension has seven classes — minimum deposit, typical, at the maximum effective balance, above the maximum effective balance, zero, below the minimum, and non-round (with extra gwei) — each with boundary values. The builder registry state dimension has boundaries at an empty registry, a single builder, and a registry near or at the `BUILDER_REGISTRY_LIMIT`. The pending deposits list has boundaries at empty, near the limit, and at the limit.

The eq-partition found 23 meaningful scenario combinations for `process_deposit_request`. Of those, 17 were already covered by the 28 existing tests (11 Electra tests for the validator deposit path and 17 Gloas tests for builder deposits, top-ups, and routing), and 6 were gaps — 74% scenario coverage. The gaps were: zero-amount deposits, below-minimum deposits, empty builder registry, pending deposits near or at the limit, and the multiple-reusable-slots scenario for builder index allocation. All 6 are addressed in [PR #4906](https://github.com/ethereum/consensus-specs/pull/4906) (two were omitted in the end because reaching the registry limits would have required very large test fixtures).

### Common observations across the three functions

| Function | Structure | Scenarios coverage | Tests | Spec bug found? |
|----------|-----------|--------------------|-------|-----------------|
| `process_proposer_slashing` | Sequential asserts | 18/25 (72%) | [PR #4871](https://github.com/ethereum/consensus-specs/pull/4871) — 20 tests | No |
| `process_withdrawals` | Multi-phase pipeline | N/A (analysis focused on the input space) | [PR #4830](https://github.com/ethereum/consensus-specs/pull/4830) — 29 tests | **Yes** ([PR #4835](https://github.com/ethereum/consensus-specs/pull/4835)) |
| `process_deposit_request` | Routing logic | 17/23 (74%) | [PR #4906](https://github.com/ethereum/consensus-specs/pull/4906) — 14 tests | No |

The same method was applied to three different function structures with consistent results. It is not limited to sequential validation pipelines. It applies to any function where the code's branching, conditions, and iteration patterns define the partition structure — which is any function in the consensus specs.

## Scaling with AI Prompts

The spec-docs and eq-partition documents in this post were all generated with AI assistance. Each one states this at the top: "*This report is AI-generated and is not an authoritative source of truth.*" The human role was to give the right inputs, validate the outputs, and make priority decisions. The AI ran the procedure.

This works because the two-step method is algorithmic. It has well-defined inputs, well-defined outputs, and a clear procedure at each step. The expertise is in the method — in the rules for finding partition dimensions from code constructs, listing classes, and computing boundary values — not in Ethereum domain knowledge. An AI that has never seen a consensus spec can run the procedure correctly, if the instructions are precise enough.

### Required inputs for each prompt

For [Step 1 (spec-doc generation)](https://notes.ethereum.org/@leolara/prompt-spec-doc), the prompt gives the function source code, the source of every helper it calls (found by walking the call tree), the container type definitions (`BeaconState`, `ProposerSlashing`, `Validator`, etc.), the relevant constant tables, and the existing test file. It asks for a structured document with specific sections: input fields table (field, type, value range, cross-field constraints, purpose), output fields table (field, modification), validation conditions (each `assert` with its check and failure cause), call tree, key constants, and existing test inventory grouped by category.

For [Step 2 (eq-partition analysis)](https://notes.ethereum.org/@leolara/prompt-eq-partition), the prompt gives the Step 1 spec-doc as its only context. It asks for: one partition dimension per validation condition, per branch, and per sub-condition from inlined helpers; classes per dimension with valid/invalid labels; boundary values (ON/IN/OUT) for every numeric comparison; a cross-product combination table reduced to meaningful combinations; a mapping of existing tests to combinations; and gap identification with suggested test names and expected outcomes.

The two-step split is essential. Each prompt has a focused scope and a clear deliverable. The AI does not need to hold the whole analysis in context at once — Step 1 produces the map, Step 2 reads it and partitions it. This split also makes validation easier: the spec-doc can be reviewed against the source code, and the eq-partition against the spec-doc, each step checked on its own.

### Suitability for AI assistance

The method is mechanical in a way that fits AI strengths and avoids AI weaknesses. Listing every field a function reads, every `assert` condition, tracing a call tree, building a table of partition classes — these are exhaustive, structured tasks where the risk of hallucination is low, because every claim can be checked against the source code. The output format (tables, matrices, mappings) is constrained enough that errors are visible on inspection.

Compare this with the request "write tests for this function." That asks the AI to decide *which scenarios are relevant* — a judgment that depends on domain knowledge, threat modeling, and experience with real client bugs. The AI may produce plausible tests that cover the obvious cases and miss the subtle ones, with no systematic way to tell what was omitted. The two-step method removes this problem by making the "what to test" question mechanical and auditable, and then reducing the "write the test" step to implementing a well-specified scenario.

### Limitations

The method has real limits. **Priority assignment** is the biggest: the eq-partition finds all gaps, but it cannot rank them. An expert knows that "slots differ within the same epoch" (a validation logic gap) matters more than "empty payment slot when older than two epochs" (a no-op edge case). The human reviewer provides this judgment; the method produces the complete list, the human decides where to spend effort.

**Opaque functions** are a second limit. BLS signature verification, for example, becomes a boolean predicate in the analysis: valid or invalid. This is enough for enumerating scenarios (tests needed with valid and with invalid signatures), but the method cannot generate actual BLS test data — that needs cryptographic tooling, outside the partition analysis.

**Cross-function interactions** are a third limit. The method analyzes one function at a time. Questions like how slashing interacts with epoch processing, or how withdrawal ordering affects later block validation, need system-level analysis that the function-level technique does not provide. The method complements integration testing; it does not replace it.

## The Loop Case: `process_attester_slashing`

The three functions so far — `process_proposer_slashing`, `process_withdrawals`, and `process_deposit_request` — have branches, conditionals, and multi-phase pipelines, but none has a `for` loop with a conditional body that produces different behavior depending on the elements it sees across iterations. `process_attester_slashing` has such a loop. It introduces a new kind of partition dimension: iteration behavior.

The function validates two attestations, checks that their data is slashable (double vote or surround vote), computes the intersection of their attesting indices, then iterates over that intersection:

```python
slashed_any = False
for index in sorted(set(indices_1) & set(indices_2)):
    if is_slashable_validator(state.validators[index], get_current_epoch(state)):
        slash_validator(state, index)
        slashed_any = True
assert slashed_any
```

The loop body calls `is_slashable_validator` on each validator in the intersection. Some may be slashable, others not (already slashed, not yet activated, or already withdrawable). The variable `slashed_any` starts as `False`, is set to `True` if any validator is actually slashed, and is asserted after the loop. If no validator is slashed, the whole operation fails.

The naive approach — unrolling the loop for every intersection size and validator state combination — explodes combinatorially. [CrossHair](https://github.com/pschanely/CrossHair), the symbolic execution tool, generates more than 42 concrete test cases for this function by exploring different list lengths and element positions. But most are redundant: `[validator_6, validator_9]` with both slashable is the same equivalence class as `[validator_2, validator_5]` with both slashable. The concrete details differ; the behavior is identical.

The partition approach is different. Following Gaudel's framework, where loop bodies are treated as opaque nodes with their own partition structure, the loop iteration is classified into a few behavioral classes:

**Zero iterations**: the intersection is empty. The body never runs. `slashed_any` stays `False`. The final `assert slashed_any` fails. This is one equivalence class, whatever the reason for the empty intersection (disjoint index sets, an empty attestation, etc.).

**All uniform — all slashable (∀ slashable)**: every validator in the intersection passes `is_slashable_validator`. All are slashed. `slashed_any` is set to `True`. The assert passes.

**All uniform — none slashable (∀ not slashable)**: every validator fails `is_slashable_validator`. None are slashed. `slashed_any` stays `False`. The assert fails.

**Mixed (∃ slashable ∧ ∃ not slashable)**: some validators are slashable, others not. The slashable ones are slashed, the rest skipped. `slashed_any` is set to `True`. The assert passes. This is the most common real scenario.

Combined with the pre-loop validation checks (is the attestation data slashable? is attestation 1 valid? is attestation 2 valid?), the full analysis produces 7 scenarios:

| # | Scenario | Outcome |
|---|----------|---------|
| S1 | Attestation data not slashable | AssertionError |
| S2 | Attestation 1 invalid | AssertionError |
| S3 | Attestation 2 invalid | AssertionError |
| S4 | Empty intersection of indices | AssertionError |
| S5 | All validators slashable | Success |
| S6 | No validators slashable | AssertionError |
| S7 | Mixed — some slashable, some not | Success |

Seven scenarios, against CrossHair's 42. Both cover the same behavioral space, so the gain is not precision. It is that the 7 scenarios are *named*, *classified*, and *auditable*. A reviewer can check each one against the spec code and confirm the enumeration is complete. The 42 concrete cases are a flat list of inputs, with no sign of which behavioral class each belongs to and no sign of whether all classes are represented.

### The flag-latch pattern

The `slashed_any` variable is an example of a pattern common in imperative code: a boolean flag set before a loop, conditionally set inside the loop, and checked after. This "flag-latch" pattern creates data-flow constraints that remove certain partition classes as infeasible.

For example, "zero iterations AND `slashed_any == True`" is impossible — if the loop never runs, the flag cannot be set. Likewise, "all iterations skip the slashing condition AND `slashed_any == True`" is impossible — if no iteration sets the flag, it stays `False`. These constraints are invisible to a purely propositional analysis (where Z3 treats `slashed_any` as an unconstrained boolean). They require tracking the data flow: the flag starts at `False`, can be set to `True` only inside the loop body's conditional branch, and is never reset.

Recognizing this pattern removes 4 infeasible classes from the raw partition, reducing the count from 11 to the final 7. The pattern generalizes to any loop with a latch variable — counters, accumulators, "found" flags — which are common in spec functions that iterate over validator sets.

## Implications for the Consensus-Specs Testing Ecosystem

The new tests and the spec bug are useful by themselves. But the consensus-specs testing effort now also has something it did not have before: a systematic, reproducible way to answer "how complete are our tests for this function?"

Today, when you ask whether the test suite for `process_proposer_slashing` is adequate, the most accurate answer is that it is a matter of judgment. The expert who wrote the tests believes they covered the important cases. A reviewer may agree. But neither can point to a document that lists every meaningful input scenario and shows which are tested and which are not. The partition analysis produces exactly that document. For `process_proposer_slashing`, the [answer](https://notes.ethereum.org/@leolara/eq-partition-proposer-slashing) is precise: 25 meaningful combinations, 18 covered, 7 gaps — 72% scenario coverage. For [`process_deposit_request`](https://notes.ethereum.org/@leolara/eq-partition-process_deposit_request), it is 23 combinations, 17 covered, 6 gaps — 74% scenario coverage. This metric has a denominator derived from the spec itself, not the implementation, and it is a number you can track, compare across functions, and improve over time.

This matters during hard forks. When an EIP changes a spec function, the function gains new partition dimensions. The Gloas fork added builder payment deletion logic to `process_proposer_slashing` — three new timing classes and two new payment-state classes, producing six new combinations in the cross-product table. It introduced a new builder withdrawal pipeline in `process_withdrawals`. It added routing logic to `process_deposit_request`. In each case, re-running the two-step analysis on the changed function shows immediately which dimensions are new and which combinations lack tests. You do not have to guess which parts changed enough to need new tests — the analysis makes it explicit.

The spec bug found during the `process_withdrawals` analysis shows a less obvious benefit. Systematic input-space documentation forces the analyst to trace every field the function reads through every code path that reads it. When the spec-doc traced the call to `update_next_withdrawal_validator_index`, it became clear this Capella-era function was receiving a `ValidatorIndex` that could now hold a `BUILDER_INDEX_FLAG` — a value it was not designed for. This was not a test gap; it was a defect in the spec itself, invisible to anyone not systematically cataloging the input space.

The artifacts the method produces — the spec-doc and the eq-partition — have value apart from the tests they generate. They are version-controllable documents that can be reviewed, updated when the spec changes, and shared with anyone who needs to understand what a function does and the state of its test coverage. The [spec-doc for `process_withdrawals`](https://notes.ethereum.org/@leolara/test_process_withdrawals) went directly into [PR #4830](https://github.com/ethereum/consensus-specs/pull/4830) with the test file, giving the reviewer a structured map of the function's input/output space. This is a different kind of documentation from code comments or README files — it is a testable model of the function, kept with the tests it informs.

Finally, the method complements the other techniques in the toolbox. Fuzzing finds unpredicted crashes and disagreements. Property-based testing checks invariants across random samples. Manual expert tests cover scenarios that need deep protocol knowledge even to imagine. Partition analysis fills a gap none of these address: the systematic enumeration of every meaningful input scenario derived from the spec's own structure. It does not replace human judgment; it gives human judgment a complete list to work from.

## Future Direction: AI Coding Agents and Systematic Test Generation

The "Scaling with AI Prompts" section described how AI assists with the analysis — generating spec-docs and eq-partitions. There is a further step: using AI coding agents to generate the test code itself. The two-step method is not only a way to help humans write tests faster. It produces exactly the kind of structured, unambiguous specification that an AI coding agent needs to generate test code reliably.

### Limitations of the "write tests for this function" instruction

When an AI coding agent gets a spec function and the instruction to "write tests," it faces the same problem as a human expert: it must decide which scenarios are relevant. Without a systematic framework, it generates tests for the obvious cases — the happy path and a few error paths — and misses the same subtle combinations humans miss. The output is unpredictable and hard to audit. You cannot look at the generated tests and tell whether the agent covered all scenarios or only the simple ones. AI agents are good at generating code from specifications, but they need a specification of *what* to generate.

### The partition table as an agent specification

The eq-partition changes this. Each row in the coverage table defines one test scenario with explicit conditions. Each gap has a suggested test name, the partition classes it exercises, and the expected outcome. Boundary values give exact numeric inputs. The spec-doc provides all the context the agent needs: field types, value ranges, constants, helper functions, and container definitions.

This changes the agent's task from "decide what to test" — a creative, error-prone judgment — to "implement this specific test scenario given these constraints" — a mechanical, verifiable code generation task. The agent gets an instruction like: "Write `test_invalid_slots_same_epoch_different_slot`: `header_1.slot = epoch_start_slot`, `header_2.slot = epoch_start_slot + 1`, same `proposer_index`, headers differ in `body_root`. Expected: `AssertionError` on the slot equality check." This is a well-defined specification. The agent does not need to know why the scenario matters or how it relates to consensus safety. It needs to translate the specification into code that follows the existing test patterns in the codebase.

### A three-stage pipeline

The full workflow has three stages, each with a different balance of AI and human contribution.

In the first stage — **analyze** — the AI generates the spec-doc and eq-partition using the structured prompts from "Scaling with AI Prompts". The human reviews and validates the partition analysis, checking each dimension against the spec code and confirming the enumeration is complete. This is where errors in the analysis are caught: a missing dimension, a misclassified boundary, or an infeasible combination that should have been removed.

In the second stage — **prioritize** — the human reviews the gap table and assigns priorities. This is where domain expertise matters most. The method finds all gaps mechanically, but an expert knows "slots differ within the same epoch" is higher priority than "empty payment slot when the epoch is older than two epochs." The method produces the complete list; the human decides where to invest.

In the third stage — **implement** — an AI coding agent generates the test code for each prioritized gap, using the matching eq-partition row as its specification and the spec-doc as context. The agent follows the existing test patterns in the codebase — for `process_proposer_slashing`, the `prepare_process_proposer_slashing` and `assert_process_proposer_slashing` helpers, which structure each test's setup and expectations.

The systematic method is what makes the agent trustworthy. Because the partition analysis is auditable — each dimension can be checked against the spec code — and because each generated test targets a specific, well-defined scenario, the human can verify coverage by reviewing the partition table instead of reading every line of generated test code. The review question shifts from "did the AI write good tests?" to "does the partition table correctly capture the function's input space?" The first is hard to answer. The second is straightforward.

### Relevance to hard fork testing at scale

Each Ethereum hard fork changes dozens of spec functions. The current process — experts writing tests function by function — is a bottleneck. The test-writing work for the three functions in this post needed weeks of iteration per function. With the three-stage pipeline, the analysis step can run across all changed functions in parallel. The partition tables show immediately which functions have the largest coverage gaps, so the team can prioritize. AI agents can draft the test implementations for the prioritized gaps. Human reviewers focus on validating the partition logic and the highest-priority tests, instead of writing boilerplate setup code.

This does not replace human judgment. It moves human judgment to where it is most valuable — partition validation and priority decisions — and automates the mechanical parts. The goal is not "AI writes all the tests." The goal is that every spec function has a documented, auditable, complete enumeration of its test scenarios, and that turning those scenarios into executable tests becomes the simpler part of the process.

## Conclusion

The Ethereum consensus specs are executable Python that defines the protocol's behavior. Every client must reproduce these functions exactly. Domain experts write the test suite that enforces this, and the tests cover the protocol well — but until now there was no systematic way to answer: for a given function, how many distinct input scenarios exist, and how many are tested?

This post described a two-step technique that answers this. Step 1 documents the function's input/output space — every field read, every field modified, every validation condition, and every helper called. Step 2 applies equivalence partitioning to derive every meaningful scenario and maps existing tests against the result. The gap between what should be tested and what is tested becomes explicit, auditable, and actionable.

Applied to `process_proposer_slashing`, the method found 25 meaningful input combinations, of which 18 were tested — 72% scenario coverage, with 7 gaps. Six of those gaps, plus 14 boundary value tests targeting the 5 untested and 10 implicitly-covered boundaries, produced 20 new tests, raising scenario coverage to 96%. Applied to `process_withdrawals`, the input-space analysis revealed a spec bug — a Capella-era function that did not handle the `BUILDER_INDEX_FLAG` added in the Gloas fork. Applied to `process_deposit_request`, the same method handled a structurally different function (routing logic instead of sequential validation) and found further gaps. Three functions, three different code structures, consistent results.

The method works because the consensus specs already are a formal model — they just need to be read this way. Every `assert` is a partition boundary. Every `if` branch is a dimension. Every `for` loop with a conditional body adds iteration-behavior classes. Every inlined helper expands the dimension space. The spec holds all the information needed to enumerate its own test scenarios.

The systematic output — structured partition tables with concrete gap descriptions and boundary values — is also exactly what AI coding agents need to generate test code reliably. The method changes the agent's task from "decide what to test" to "implement this specific scenario." The human reviews the partition table; the agent writes the code. This three-stage pipeline — analyze, prioritize, implement — scales to the dozens of functions changed in each hard fork.

The method can be applied immediately. The procedure: select a spec function, document its input/output space, partition it, map the existing tests, and identify the gaps. The method is algorithmic, the tools are structured AI prompts, and the results — new tests across three functions and a spec bug found during the analysis — are concrete.
