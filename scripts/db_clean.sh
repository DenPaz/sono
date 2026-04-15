#!/usr/bin/env bash
set -euo pipefail

echo "  Cleaning database..."
uv run manage.py flush --noinput
echo "  Database cleaned."
