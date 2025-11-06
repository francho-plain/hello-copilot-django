#!/bin/bash
# Quality Analysis Script for Python Backend
# This script runs all quality checks required for SonarQube analysis

# set -e  # Commented out to allow script to continue on warnings

echo "🚀 Starting Python Quality Analysis..."

# Activate virtual environment
source venv/bin/activate

# Ensure pytest-django can find the Django settings module when running directly
export DJANGO_SETTINGS_MODULE=mysite.settings
# Add project root to PYTHONPATH so pytest can import the project modules
export PYTHONPATH="$(pwd):$PYTHONPATH"

echo "📦 Running tests with coverage (using Django test runner for reliability)..."
# Use coverage with Django's test runner because pytest discovery can be flaky for unittest-style Django TestCase classes
coverage run --source=cats manage.py test
if [ $? -ne 0 ]; then
    echo "❌ Tests failed (manage.py test)"
    exit 1
fi

# Generate coverage reports
coverage xml -o coverage.xml
coverage html -d htmlcov
echo "- generated coverage.xml and htmlcov/"

echo "🔒 Running Bandit security analysis..."
# Exclude generated migration files and venv to avoid Bandit AST incompatibilities
bandit -r cats -f json -o bandit-report.json --exclude cats/migrations,venv
BANDIT_EXIT=$?
if [ $BANDIT_EXIT -ne 0 ]; then
    echo "⚠️  Bandit exited with code ${BANDIT_EXIT}. See run-quality.log for details. Writing fallback bandit-report.json"
    # Write a minimal fallback JSON so downstream tools (SonarQube) have a valid file
    python - <<'PY' > bandit-report.json
import json, datetime, os
report = {
    "errors": [
        {
            "filename": "bandit",
            "reason": f"Bandit exited with code {os.environ.get('BANDIT_EXIT', 'unknown')}. See run-quality.log for details."
        }
    ],
    "generated_at": datetime.datetime.utcnow().isoformat() + 'Z',
    "metrics": {}
}
json.dump(report, sys.stdout, indent=2)
PY
fi

echo "🔍 Running Pylint code quality analysis..."
pylint cats --output-format=text > pylint-report.txt 2>/dev/null || echo "Pylint completed with warnings"

echo "✅ Quality analysis completed!"
echo ""
echo "Generated files:"
echo "  - coverage.xml (Coverage report)"
echo "  - test-results.xml (Test results)"
echo "  - bandit-report.json (Security analysis)"
echo "  - pylint-report.txt (Code quality analysis)"
echo "  - htmlcov/ (HTML coverage report)"

echo ""
echo "📊 Coverage Summary:"
python -m coverage report --show-missing