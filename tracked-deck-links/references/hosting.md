# Hosting the tracker for real use

The server is one Node process: `app/server.mjs`. It listens on `127.0.0.1:<port>` and keeps everything
in `$DECKLINKS_HOME`. Recipients need HTTPS, so put a reverse proxy in front of it. If the host already
runs nginx or Caddy, use that.

Replace the placeholders (`<user>`, `<skill-dir>`, `<home>`, `decks.example.com`) with the user's values.
Ask the user before touching an existing web server config. Back up the file first, and test the config
(`nginx -t`, `caddy validate`) before you reload.

## 1. Configure for the public address

```bash
export SKILL=<skill-dir> DECKLINKS_HOME=<home>
node "$SKILL/scripts/decklinks.mjs" init --port 8787 --public-origin https://decks.example.com
# under a path of an existing site instead of its own (sub)domain:
node "$SKILL/scripts/decklinks.mjs" init --port 8787 --public-origin https://example.com --prefix /deck
```

## 2. systemd service (Linux)

`/etc/systemd/system/decklinks.service`:

```ini
[Unit]
Description=Tracked deck links
After=network.target

[Service]
User=<user>
Environment=DECKLINKS_HOME=<home>
ExecStart=/usr/bin/node --disable-warning=ExperimentalWarning <skill-dir>/app/server.mjs
Restart=on-failure
NoNewPrivileges=yes
ProtectSystem=strict
ReadWritePaths=<home>
PrivateTmp=yes

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload && sudo systemctl enable --now decklinks
systemctl status decklinks --no-pager; curl -s http://127.0.0.1:8787/healthz
```

`<skill-dir>` must not be under a home directory if you add `ProtectHome=yes`. If it is, copy `app/`
and `scripts/` to `/opt/decklinks` first. Publish and mint commands keep working, because they only
need `$DECKLINKS_HOME` and the running server.

On hosts without systemd (a PaaS, a container), run `node app/server.mjs` as the start command. Set
`DECKLINKS_HOME` to a persistent volume, and set `HOST=0.0.0.0` if the platform's proxy connects over
the network. Env vars override `config.json`: `PORT`, `HOST`, `PREFIX`, `PUBLIC_ORIGIN`, `SHELL_TITLE`,
`NTFY_TOPIC`, `NTFY_SERVER` and `ADMIN_PASSWORD_FILE`.

## 3a. nginx

Own subdomain:

```nginx
server {
    server_name decks.example.com;
    # listen 443 ssl; ssl_certificate ...;  (certbot adds these)
    location / {
        proxy_pass http://127.0.0.1:8787;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-Proto https;
        client_max_body_size 128k;
    }
}
```

Under a path of an existing site, after `init --prefix /deck`, add this to that site's `server` block:

```nginx
location ^~ /deck/ {
    proxy_pass http://127.0.0.1:8787;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-Proto https;
    client_max_body_size 128k;
}
```

## 3b. Caddy

```caddy
decks.example.com {
    reverse_proxy 127.0.0.1:8787 {
        header_up X-Real-IP {remote_host}
    }
}
```

Under a path: `handle /deck/* { reverse_proxy 127.0.0.1:8787 { header_up X-Real-IP {remote_host} } }`.
Use `handle`, not `handle_path`: the tracker expects to see the prefix.

## 4. Check from outside

```bash
curl -s https://decks.example.com/healthz                  # {"ok":true,"decks":{...}}
curl -s -o /dev/null -w '%{http_code}\n' https://decks.example.com/d/doesnotexist   # 404
```

Then mint a throwaway link and open it on a phone. Run `report` to check that it shows as opened,
then revoke the link.

## Notes

- Every response carries `Cache-Control: no-store`. A CDN in front, such as Cloudflare, will not cache
  links or beacons, so no extra rules are needed.
- The tracker trusts `X-Real-IP` for the visit IP. Keep it bound to `127.0.0.1` behind the proxy.
- Backups: copy `$DECKLINKS_HOME`. For a consistent copy of a live database, use
  `sqlite3 tracker.db ".backup backup.db"`, or stop the service while you copy.
- Moving hosts: copy `$DECKLINKS_HOME`, start the server and point DNS at it. Links keep working because
  the tokens live in the database.
