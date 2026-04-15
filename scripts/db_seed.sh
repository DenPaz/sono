#!/usr/bin/env bash
set -euo pipefail

echo "  Seeding database with development data..."
uv run manage.py update_site
uv run manage.py create_test_superusers
# Remove evaluations first to avoid PROTECT errors when cleaning users.
uv run manage.py shell -c "from apps.assessments.models import AssessmentEvaluation; AssessmentEvaluation.objects.all().delete()"
uv run manage.py create_test_users --clean
uv run manage.py create_default_professional_user
uv run manage.py seed_assessments_data --clean
echo "  Development data seeded."
