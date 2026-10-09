# Secrets on the agent box

Read this for step 6. A secret is an API key, token, password or private key. The rule:

**The command that needs a secret fetches it when it runs, and the secret goes nowhere else.**

Not into a Claude chat. Not into CLAUDE.md, notes, READMEs, code or `.env` files inside a git repo.
Not typed on a command line that is saved in shell history. Not into logs or screenshots.

Why: anything in a chat is stored in the conversation; anything in a file can be read by the agent,
copied into a commit, or pushed somewhere public by mistake.

## Option A: macOS Keychain (built in, nothing to install)

Store a secret. The command prompts for the value, so it is never visible on the command line:

```bash
security add-generic-password -a "$USER" -s OPENAI_API_KEY -w
```

(`-s` is the name you give it. Running it again for the same name fails; add `-U` to replace it.)

Use it for exactly one command:

```bash
OPENAI_API_KEY="$(security find-generic-password -a "$USER" -s OPENAI_API_KEY -w)" python3 my_script.py
```

The key exists only inside that command's environment, and only the command line *with the
`$(...)` part* is saved in history, not the key itself.

A helper to make this shorter. Add to `~/.zshrc` on the box:

```bash
with-secret() {   # usage: with-secret NAME command args...
  local name="$1"; shift
  env "$name=$(security find-generic-password -a "$USER" -s "$name" -w)" "$@"
}
```

Then: `with-secret OPENAI_API_KEY python3 my_script.py`.

Over SSH the Keychain may be locked; unlock it first with
`security unlock-keychain ~/Library/Keychains/login.keychain-db` (it prompts).

To see stored keys, open the Keychain Access app and search for the name. Remove one: `security delete-generic-password -a "$USER" -s OPENAI_API_KEY`.

## Option B: a password manager CLI

Good if the owner already uses 1Password or Bitwarden, and nice because keys can be changed in one
place for all machines.

**1Password** (`brew install 1password-cli`, then sign in following its instructions). Put *references*
in a file, not values. A reference looks like `op://Vault/Item/field` and is safe to keep in a file:

```bash
# ~/work/project/secrets.env  (contains references only, no secret values)
OPENAI_API_KEY=op://Agent Box/OpenAI/credential
```

```bash
op run --env-file ~/work/project/secrets.env -- python3 my_script.py
```

Create a separate vault (for example "Agent Box") holding only the keys this box needs, so the agent
never has access to the owner's personal passwords.

**Bitwarden Secrets Manager** works the same way with `bws run -- <command>`; see its docs.

## Tell Claude what to do, not the secret

In CLAUDE.md (see the template), describe *how* to get a secret: "OpenAI key: `with-secret
OPENAI_API_KEY <command>`". The agent can then use keys without ever seeing them in chat.

Also stop Claude Code from opening key files by accident. In `~/.claude/settings.json` of the user Claude runs as (normally `owner`):

```json
{
  "permissions": {
    "deny": [
      "Read(./.env)",
      "Read(./.env.*)",
      "Read(~/.ssh/**)",
      "Read(~/.config/op/**)"
    ]
  }
}
```

If the file already exists, merge the `deny` list into it instead of replacing the file.

## Shell history hygiene

- In zsh (the Mac default), a command that **starts with a space** is not saved if this option is on.
  Add to `~/.zshrc`: `setopt HIST_IGNORE_SPACE`.
- If a secret was typed on a command line anyway: remove that line from `~/.zsh_history` with a text
  editor, and treat the secret as leaked (below).

## If a secret leaks

It leaked if it appeared in a chat, a file in a git repo, a screenshot, a log or shell history.

1. Create a new key at the provider and revoke the old one. Deleting the file is not enough.
2. Store the new key in the Keychain or password manager.
3. If it reached a git repo, assume it is public even if you delete the commit.
