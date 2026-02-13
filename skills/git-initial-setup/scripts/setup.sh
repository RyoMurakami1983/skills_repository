#!/usr/bin/env bash
# Install pre-commit and pre-push hooks into the current repository.

set -euo pipefail

repo_root=$(git rev-parse --show-toplevel 2>/dev/null || true)
if [ -z "$repo_root" ]; then
    echo "❌ Not inside a git repository."
    exit 1
fi

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
hook_dir="$repo_root/.git/hooks"

mkdir -p "$hook_dir"
cp "$script_dir/pre-commit" "$hook_dir/pre-commit"
cp "$script_dir/pre-push" "$hook_dir/pre-push"
chmod +x "$hook_dir/pre-commit" "$hook_dir/pre-push"

echo "✅ Installed pre-commit and pre-push hooks to $hook_dir"
