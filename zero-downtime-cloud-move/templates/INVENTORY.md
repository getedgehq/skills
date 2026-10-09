# Inventory: <app>, verified <date>

Every row needs evidence: the command that produced it, run today. No row from memory.

## Entry points

| Hostname | Resolves to | Served by | TTL | Evidence |
| --- | --- | --- | --- | --- |
| app.example.com | | | | `dig +noall +answer app.example.com` |
| api.example.com | | | | |

## Compute

| Service | Live revision or image | CPU / memory | Scaling | Request timeout | Evidence |
| --- | --- | --- | --- | --- | --- |
| | | | | | |

## Configuration (names only, never values)

| Setting or secret name | Used for | Tied to old cloud? | Where the value lives |
| --- | --- | --- | --- |
| | | | |

## Data

| Store | Kind | Size / object count | Moves? | Evidence |
| --- | --- | --- | --- | --- |
| | database | | | |
| | object storage | | | |
| | queue / cache / cron | | | |

## Outbound dependencies

| Dependency | Called from | Tied to old cloud? | Replacement | Switch (one setting) |
| --- | --- | --- | --- | --- |
| | | | | |

## DNS

- Zone hosted at:
- Full zone export saved to:
- Records that will change (old value, new value, TTL):

## Traffic shape

- Requests, last 30 days:
- Peak hour:
- Longest real request or stream:
- Background and scheduled jobs:

## Limits that constrain the target

| Need (from real traffic) | Target service limit | Fits? |
| --- | --- | --- |
| Longest request: | | |
| Largest upload: | | |

## Top three risks

1.
2.
3.
