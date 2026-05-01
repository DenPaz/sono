---
name: upgrade-js-deps
description: Upgrade JavaScript dependencies using npm-check-updates, then run post-upgrade checks to ensure nothing is broken.
allowed-tools:
  [
    Bash(npx npm-check-updates *),
    Bash(make npm-install *),
    Bash(make npm-build *),
    Bash(make test *),
    Bash(make lint *),
  ]
---

## Your task

Upgrade all JavaScript dependencies and verify nothing is broken.

### Step 1: Check for available upgrades

Run `npx npm-check-updates` to see what upgrades are available. Review the output and
present the list to the user.

Pay particular attention to **major version bumps** — list them separately and call out
anything that may need migration work (e.g. Tailwind, DaisyUI, Vite, Alpine.js, HTMX).
Ask the user whether to proceed with major bumps before continuing.

### Step 2: Update package.json

Run `npx npm-check-updates -u` to update `package.json` with the new versions.

If the user asked to skip specific majors in Step 1, use the `--reject` flag accordingly,
e.g. `npx npm-check-updates -u --reject tailwindcss,daisyui`.

### Step 3: Install updated dependencies

Run `make npm-install` to install the upgraded dependencies and update `package-lock.json`.

### Step 4: Run post-upgrade checks

Run these checks sequentially, stopping if any step fails:

1. **Build**: Run `make npm-build` to verify the production build still works. Watch for
   new warnings — Vite/Rollup will surface deprecations here.
2. **Tests**: Run `make test` to verify the Django test suite still passes. (Frontend
   bundles are loaded by some integration tests via `django-vite`.)
3. **Lint**: Run `make lint` so prettier and djlint can flag any formatting drift caused
   by new tooling versions.

This project does not use TypeScript, so there is no separate type-check step.

### Step 5: Summarize

Summarize what was done:

- Which packages were upgraded (notable version changes — group major / minor / patch).
- Whether the build succeeded and any new warnings.
- Whether all tests passed.
- Any lint issues introduced.
- Anything that needs manual attention (e.g. DaisyUI theme tokens that changed names,
  Vite plugin API changes, etc.).

If there were failures, present the issues and ask how the user wants to proceed.

If everything passed, ask the user if they'd like to commit the changes. If yes, hand off
to the `commit` skill — suggest a subject line like `chore(deps): upgrade JavaScript dependencies`.
