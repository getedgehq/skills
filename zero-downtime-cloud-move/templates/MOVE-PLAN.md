# Move plan: <app> from <old cloud> to <new cloud>

Rules: verify, do not remember. Parallel, not in place. One-line rollback per phase. Real workloads before the switch. Decommission last.

Needs the human's go: the traffic switch, deleting data, deleting old resources, closing accounts.

| Phase | Status | Rollback (one line, written before starting) | Evidence it is done |
| --- | --- | --- | --- |
| 1. Inventory | todo | nothing changed | INVENTORY.md complete |
| 2. Decouple behind one switch | todo | unset `<SETTING>` | suite identical on base and branch; works with old credentials removed |
| 3. Build new stack in parallel | todo | delete the new stack (`<script> destroy`) | healthy; reaches database and dependencies |
| 4a. Real workloads on the new stack | todo | none needed, no traffic moved | runs listed below |
| 4b. Switch traffic and watch | todo | paste old DNS values: `<record> <old value>` | window numbers below |
| 5a. Copy data | todo | set `<STORAGE SETTING>` back to the old store | N of N, second pass 0 |
| 5b. Decommission old cloud | todo | none: this is why it is last | provider inventory shows zero for this app |

## Real workload runs (phase 4a)

| What ran | Against | Duration | Result | Output landed in |
| --- | --- | --- | --- | --- |
| | new stack, direct | | | |
| | new stack, through the frontend path | | | |

## Watch window (phase 4b)

- Switched at:
- Window length:
- Requests on the new side:
- Server errors on the new side:
- Requests on the old side:
- Real workload through the public hostname:

## Data copy (phase 5a)

- Writer switched to the new store at:
- First pass: copied ___ of ___
- Second pass: ___ left (must be 0)
- Source count / destination count:
- Real file read through the app:

## Decommission (phase 5b)

| Resource | Deleted at | By | Evidence |
| --- | --- | --- | --- |
| | | | |

Left on purpose (belongs to another product):

## Decisions and surprises

- <date>: <what changed in the plan and why>
