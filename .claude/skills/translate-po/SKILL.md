---
name: translate-po
description: Auto-discover all non-English languages from config/settings/base.py and translate every untranslated string in their .po files using the Claude API, then compile the messages.
allowed-tools:
  [
    Read,
    Write,
    Bash(make translations *),
    Bash(uv run manage.py compilemessages *),
  ]
---

## Your task

Automatically discover all languages configured in the project, then translate every
untranslated `msgstr ""` entry in their `.po` files using the Claude API, and finally
compile the messages so the translations take effect.

---

### Step 1: Discover the configured languages

Read `config/settings/base.py` and parse the `LANGUAGES` list, for example:

```python
LANGUAGES = [
    ("en", _("English")),
    ("pt-br", _("Portuguese")),
]
```

**Always skip `"en"`** — English is the source language of the codebase (all `msgid` strings
are written in English) so it never needs a translation file.

Collect all remaining language codes. For the example above the result would be: `["pt-br"]`.

If only English is configured, report that there is nothing to translate and stop.

---

### Step 2: Find the .po files for each language

Django maps language codes to locale directory names by replacing `-` with `_` and
uppercasing the region suffix, e.g. `pt-br` → `pt_BR`, `fr` → `fr`, `es-ar` → `es_AR`.

For each non-English language code, look for these files under `locale/`:

```
locale/<locale_name>/LC_MESSAGES/django.po
locale/<locale_name>/LC_MESSAGES/djangojs.po
```

Only process files that actually exist. For each file found, count the number of entries
with an empty `msgstr ""` and report the summary to the user before proceeding:

```
Found 2 file(s) to translate:
  • locale/pt_BR/LC_MESSAGES/django.po    — 42 untranslated strings
  • locale/pt_BR/LC_MESSAGES/djangojs.po  —  3 untranslated strings
```

If all strings in all files are already translated, report that and stop.

---

### Step 3: Translate each file

Process each file with untranslated entries one at a time.

Use the Anthropic API to translate the untranslated strings, with a prompt like:

```
You are a professional software translator specialising in web application UI strings.

Translate the following Django .po file entries from English into <TARGET_LANGUAGE_FULL_NAME>.

Rules:
- Preserve ALL .po formatting exactly: comments (#), flags (#,), blank lines, and
  multiline strings split with line breaks inside the msgstr.
- Do NOT alter msgid lines — only fill in the empty msgstr values.
- Preserve Python format placeholders exactly: %(name)s, %s, %d, etc.
- Preserve HTML tags and attributes exactly — only translate visible text content.
- Keep translations natural and consistent with a modern web application.
- For entries that are identical in both languages (brand names, technical terms such as
  "Dashboard", "Admin") copy the English value unchanged.
- Return ONLY the translated .po entry blocks, with no preamble or explanation.

Entries to translate:
<untranslated blocks only>
```

If a file has more than 30 untranslated entries, split them into batches of 30, translate
each batch separately, and merge the results before writing.

---

### Step 4: Write the translated files

For each file, write the complete content back to disk:

- Fill in all previously empty `msgstr ""` values with the translations.
- Leave all metadata headers, existing translations, and comments untouched.

---

### Step 5: Compile the messages

Once all files have been written, run:

```bash
make translations
```

This re-extracts strings AND compiles. If extraction is not desired (e.g. you only want to
compile), run:

```bash
uv run manage.py compilemessages --ignore venv --ignore .venv
```

Report whether compilation succeeded or if there were any errors.

---

### Step 6: Summarise

Report:

- Which languages were processed
- How many strings were translated per file
- Whether compilation succeeded
- Any strings that may need manual review (e.g. very technical or ambiguous context)

Ask the user if they'd like to commit the changes. If yes, use the `/commit` skill.
