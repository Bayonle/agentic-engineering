#!/bin/bash
# Verification script for plugin structure

echo "🔍 Verifying Agentic Workflow Plugin Structure"
echo ""

PLUGIN_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PLUGIN_DIR"

errors=0

# Check required files
echo "📁 Checking required files..."

required_files=(
    ".claude-plugin/plugin.json"
    "README.md"
    "LICENSE"
    "CHANGELOG.md"
    "CONTRIBUTING.md"
    "skills/pm/SKILL.md"
    "skills/architect/SKILL.md"
    "skills/engineer/SKILL.md"
    "skills/qa/SKILL.md"
    "skills/deploy/SKILL.md"
    "skills/work/SKILL.md"
    "lib/task_manager.py"
    "lib/activity.py"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✓ $file"
    else
        echo "  ✗ $file (missing)"
        ((errors++))
    fi
done

echo ""

# Check SOUL templates
echo "📋 Checking SOUL templates..."

soul_files=(
    "skills/pm/assets/SOUL.md"
    "skills/architect/assets/SOUL.md"
    "skills/engineer/assets/SOUL.md"
)

for file in "${soul_files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✓ $file"
    else
        echo "  ⚠️  $file (optional but recommended)"
    fi
done

echo ""

# Check workspace template
echo "📦 Checking workspace template..."

if [ -d "lib/templates/workspace" ]; then
    echo "  ✓ lib/templates/workspace exists"

    workspace_dirs=(
        "agents/pm"
        "agents/architect"
        "agents/engineer"
        "tasks/inbox"
        "docs/specs"
        "docs/plans"
    )

    for dir in "${workspace_dirs[@]}"; do
        if [ -d "lib/templates/workspace/$dir" ]; then
            echo "    ✓ $dir"
        else
            echo "    ⚠️  $dir (will be created dynamically)"
        fi
    done
else
    echo "  ⚠️  lib/templates/workspace (will be created dynamically)"
fi

echo ""

# Check plugin.json format
echo "🔧 Validating plugin.json..."

if command -v jq &> /dev/null; then
    if jq empty .claude-plugin/plugin.json 2>/dev/null; then
        echo "  ✓ Valid JSON"

        name=$(jq -r '.name' .claude-plugin/plugin.json)
        version=$(jq -r '.version' .claude-plugin/plugin.json)
        description=$(jq -r '.description' .claude-plugin/plugin.json)

        echo "    Name: $name"
        echo "    Version: $version"
        echo "    Description: ${description:0:60}..."
    else
        echo "  ✗ Invalid JSON in plugin.json"
        ((errors++))
    fi
else
    echo "  ⚠️  jq not installed, skipping JSON validation"
fi

echo ""

# Check Python files syntax
echo "🐍 Checking Python syntax..."

for pyfile in lib/*.py; do
    if [ -f "$pyfile" ]; then
        if python3 -m py_compile "$pyfile" 2>/dev/null; then
            echo "  ✓ $(basename $pyfile)"
        else
            echo "  ✗ $(basename $pyfile) (syntax error)"
            ((errors++))
        fi
    fi
done

echo ""

# Summary
echo "="*60
if [ $errors -eq 0 ]; then
    echo "✅ Plugin structure looks good!"
    echo ""
    echo "Next steps:"
    echo "  1. Test install: claude plugin install ."
    echo "  2. Test in project: cd ~/test-project && /pm task-001"
    echo "  3. Commit: git init && git add . && git commit -m 'Initial plugin'"
    echo "  4. Push to GitHub"
else
    echo "❌ Found $errors error(s)"
    echo ""
    echo "Fix errors above before proceeding."
    exit 1
fi
echo "="*60
