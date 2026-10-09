# Cutover checklist: <app>, <date>

## Before

- [ ] Full DNS zone exported to a file: `<path>`
- [ ] Old value of every record that will change, ready to paste back:
  - `<name> <type> <old value> <ttl>`
- [ ] TTL on those records lowered to 300 seconds, at least one old TTL ago
- [ ] Certificates issued for every hostname on the new side
- [ ] Real workloads passed on the exact image that will serve (listed in MOVE-PLAN.md)
- [ ] Longest real request fits inside the new side's timeouts
- [ ] Watch commands for the new side and the old side run and return numbers now
- [ ] Rollback line written: `<one line>`
- [ ] Human said go for this exact switch

## Switch

- [ ] Changed only the traffic records (mail, verification and third-party records untouched)
- [ ] API hostname first, verified, then the site
- [ ] Time of switch noted: `<time>`

## Watch window: <N> minutes, fixed before the switch

| Minute | Requests, new side | Server errors, new side | Requests, old side |
| --- | --- | --- | --- |
| 5 | | | |
| 15 | | | |
| 30 | | | |

- [ ] One real workload run through the public hostname, passed
- [ ] Server errors on the new side: 0
- [ ] Requests on the old side: 0 by the end of the window

## Rollback rule

Server errors above the old baseline, or a failed real workload: paste the old DNS values back first, investigate second. The old stack stays up, untouched, until this window closes clean.

## After

- [ ] Window numbers written into MOVE-PLAN.md and reported to the human
- [ ] Old stack still running; decommission is a separate step with its own go
