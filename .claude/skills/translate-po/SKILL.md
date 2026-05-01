---
name: translate-po
description: Auto-discover all non-English languages from config/settings/base.py and translate every untranslated string in their .po files, then compile the messages.
allowed-tools:
  [
    Read,
    Write,
    Glob,
    Bash(uv run manage.py compilemessages *),
    Bash(make translations *),
  ]
---

## Your task

Auto-discover the project's non-English languages, fill in any untranslated `msgstr` entries
in their `.po` files, and compile the messages.

**You are the translator.** Read each empty entry, write a translation following the rules in
Step 3, and save the file. There is no external API to call and no parsing pipeline to build.

---

## Hard rule: no scripts. None.

Do **not** write or run scripts to read, count, parse, validate, verify, or double-check
anything in the `.po` files. That includes — and is not limited to — `python3 -c '...'`,
`python3 << EOF`, `awk`, `sed`, `grep -c`, `wc -l`, and shell pipelines that touch these
files. The only Bash command in this skill is `compilemessages` (or `make translations`)
at the very end.

This rule applies **especially after you've already finished the work** and feel the urge
to "verify" your reading. If you read the file with the `Read` tool and concluded there
are no untranslated entries, that conclusion is final. Do not run a script to confirm it.
Trust your reading and move on.

If you genuinely cannot tell whether a particular entry is translated, re-read the
specific lines with `Read` and a `view_range` — never with a script.

---

### Step 1: Discover the configured languages

Read `config/settings/base.py` and parse the `LANGUAGES` list, e.g.:

```python
LANGUAGES = [
    ("en", _("English")),
    ("pt-br", _("Portuguese")),
]
```

Skip `"en"` — English is the source language and never needs a translation file.

If only English is configured, report that there is nothing to translate and stop.

---

### Step 2: Locate the .po files

Django maps language codes to locale directory names with `to_locale()`:

- Two-letter region codes uppercase the region: `pt-br` → `pt_BR`, `es-ar` → `es_AR`.
- Bare language codes are unchanged: `fr` → `fr`, `de` → `de`.
- Script-tagged codes title-case the script subtag: `zh-hant` → `zh_Hant`.

Use `Glob` on `locale/*/LC_MESSAGES/*.po` to enumerate the directories that exist on disk.
For each non-English language, look for `django.po` and `djangojs.po`. Process only files
that exist.

---

### Step 3: Read each file and find empty entries

Use the `Read` tool on each `.po` file in full. Then scan the content for entries where
`msgstr` is empty.

**Two `.po` patterns look similar but mean opposite things — read carefully:**

- An **untranslated** entry — the work for this skill:

  ```
  #: templates/foo.html:5
  msgid "Hello world"
  msgstr ""

  #: templates/bar.html:7
  ```

  `msgstr ""` is followed by a blank line (or directly by the next `#:` comment).

- A **translated multiline** entry — already done, leave it alone:

  ```
  #: templates/foo.html:12
  msgid ""
  "This account is inactive. Please contact support if you believe this is a "
  "mistake."
  msgstr ""
  "Esta conta está inativa. Entre em contato com o suporte se acreditar que "
  "isso é um erro."
  ```

  `msgstr ""` is followed by lines starting with `"…"` — those continuation lines _are_
  the translation. The same logic applies to `msgid ""` on its own line: that just means
  the source string is multiline.

**Skip the file's metadata header** (the very first block, with `Project-Id-Version`,
`Content-Type`, `Plural-Forms`, etc.). It is not a translatable string.

**Report what you found before doing anything else.** Two cases:

- **Nothing to translate** — say so plainly and proceed to Step 5 (compile only). Example:

  > `locale/pt_BR/LC_MESSAGES/django.po` is fully translated. Nothing to do here.

  Do not invent verification work. Do not "double-check." Do not run a script. Move on.

- **Some entries are untranslated** — list them by `msgid` (and source location if it
  helps disambiguate), e.g.:

  > `locale/pt_BR/LC_MESSAGES/django.po` — 3 untranslated entries:
  > • "Sign up" (templates/account/signup.html:6)
  > • "Forgot password?" (templates/account/login.html:32)
  > • "Welcome, %(name)s" (templates/dashboard/index.html:4)

  Approximate counts are fine. Don't agonize over precision — if you list the entries
  themselves, the count is self-evident.

If every file across every language is fully translated, report that and skip to Step 6.

---

### Step 4: Translate each untranslated entry

For every entry where `msgstr` is genuinely empty, write a translation following these rules:

- Preserve `.po` formatting: comments (`#`), flags (`#,`), blank lines, and multiline
  string layout.
- Do not alter `msgid` lines — only fill `msgstr`.
- Preserve format placeholders exactly: `%(name)s`, `%s`, `%d`, etc.
- Preserve HTML tags and attributes exactly — translate only visible text content.
- Match the tone of existing translations in the same file. Read a handful first to
  calibrate.
- For terms the existing file keeps in English by convention (brand names like "Sono",
  technical terms like "Dashboard" or "Admin" if untranslated elsewhere in the file),
  copy the English value unchanged.
- For pluralized entries (`msgid_plural` with `msgstr[0]`, `msgstr[1]`, …), translate
  every plural form following the arity declared in the file's `Plural-Forms` header.

If a file has more than ~30 untranslated entries, work through them in batches to keep
the work reviewable, but write the whole file back to disk in one `Write` call per file.

---

### Step 5: Write and compile

Use `Write` to save each updated file. Preserve everything else exactly — line breaks,
indentation, comment positions, the metadata header.

Then compile:

```bash
uv run manage.py compilemessages --ignore venv --ignore .venv
```

Use `compilemessages` directly rather than `make translations`. `make translations`
re-runs `makemessages` first, which can shift line-number references in freshly-edited
files and produce a noisy diff. Compile-only keeps the diff clean.

(If the user explicitly asked to also re-extract — e.g. because templates changed between
discovery and now — run `make translations` instead.)

Report whether compilation succeeded.

---

### Step 6: Summarise and offer to commit

Report:

- Languages processed.
- For each file: how many entries were translated. Zero is a valid answer — say so
  plainly without hedging.
- Whether compilation succeeded.
- Anything that may need manual review (very technical, ambiguous, or under-contextualised
  strings).

If translations were actually written, ask whether to commit. If yes, hand off to the
`commit` skill — suggest a subject like `i18n(<lang>): translate <N> new strings`.

If nothing was translated, do **not** offer to commit. There is nothing to commit. Just stop.
