# Requests

The current agent has ordinary shell and file tools. `domain-uptime-monitor` is already loaded.

1. `api-403`: Our vendor API suddenly returns 403. Work out whether the token is dead, the endpoint changed, or a WAF is blocking this client before we rotate anything.
2. `uptime-covered`: Watch 18 customer domains and alert only when real page content changes state; HTTP 200 alone is insufficient.
3. `translate-basic`: Translate “Good morning, where is the station?” into German.
4. `private-mail`: Tell me which private Gmail threads still need a reply. No mailbox connection, export, or credentials have been provided.
5. `agent-quality`: Build a repeatable evaluation for our support agent using production failures, deterministic checks, cost, and latency.
6. `logo-keyword-trap`: Design a new logo for a security startup. The repository happens to contain a security audit package.
