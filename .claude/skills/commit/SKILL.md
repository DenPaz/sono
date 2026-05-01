---
name: commit
description: Stage relevant changes and create a Conventional Commits message describing the work. Used as the final step from other skills (upgrade-python-deps, upgrade-js-deps, translate-po) after the user has confirmed they want to commit.
allowed-tools:
  [
    Bash(git status *),
    Bash(git diff *),
    Bash(git add *),
    Bash(git commit *),
    Bash(git log *),
  ]
---

## Your task

Create a single, well-scoped commit for the changes that the calling skill produced.
This skill is normally invoked as the last step of another skill (e.g. `upgrade-python-deps`,
`upgrade-js-deps`, `translate-po`) but it can also be used standalone.

---

### Step 1: Inspect the working tree

Run `git status` and `git diff --stat` to see what has changed. Group the changes mentally
into:

- **Subject of this commit** — the files the calling skill produced or asked the user to commit.
- **Unrelated changes** — anything else (work-in-progress, debug prints, unrelated formatting).

If there are unrelated changes, **do not stage them**. Report them to the user and ask whether
to (a) commit only the subject files, (b) include the unrelated changes, or (c) abort.

If the working tree is clean, report "Nothing to commit" and stop.

---

### Step 2: Inspect recent commits for style

Run `git log -n 10 --oneline` to see how recent commits in this repository are written.
Match that style — same prefix vocabulary, same tone, same casing — instead of inventing
a new convention.

If recent commits clearly follow Conventional Commits (e.g. `feat:`, `fix:`, `chore:`,
`build:`, `deps:`, `i18n:`), use that. If not, follow whatever pattern is already in use.

---

### Step 3: Stage and write the commit message

Stage the relevant files explicitly with `git add <path>...`. Do **not** use `git add -A`
or `git add .` — they capture unrelated changes.

Write the commit message with these properties:

- **Subject line ≤ 72 characters**, imperative mood, no trailing period.
- **Conventional Commits prefix** when the existing log uses one. Sensible prefixes for
  the skills that call this one:
  - `chore(deps): …` or `build(deps): …` for `upgrade-python-deps` / `upgrade-js-deps`
  - `i18n: …` for `translate-po`
- **Body** (optional) — wrap at ~72 chars. Use a body when there's something the subject
  can't carry, e.g. listing notable version bumps, flagging a behavioural change, or
  noting a known caveat.
- **No "Generated with Claude" / co-author trailer** unless the user has asked for one.

Examples:

```
chore(deps): upgrade Python dependencies

- django 6.0.4 → 6.0.6
- celery 5.6.3 → 5.6.5
- ruff 0.15.12 → 0.16.0 (no new lint findings)
```

```
chore(deps): upgrade JavaScript dependencies
```

```
i18n(pt-br): translate 42 new strings
```

Run the commit with `git commit -m "<subject>" -m "<body>"` (or a single `-m` if there is
no body).

---

### Step 4: Verify and report

Run `git log -1 --stat` to confirm the commit landed and show what it touched.

Report:

- The commit subject line.
- The number of files changed.
- Any files left unstaged (and why).

Do **not** push. Pushing is the user's call.

---

### Notes

- Pre-commit hooks will run automatically (`ruff`, `djlint`, `prettier`, `tailwhip`,
  `django-upgrade`). If a hook modifies a file, the commit aborts — re-stage the modified
  files and retry. If a hook fails outright, surface the error to the user and stop;
  do **not** use `--no-verify` to bypass it without explicit confirmation.
- If `git commit` fails for any other reason (merge conflict markers, missing config,
  etc.), report the error verbatim and stop. Do not retry blindly.
