#!/usr/bin/env bash
# SKILL.md Quality Validator (Bash Wrapper)
# Validates skills by calling Python validation script
# Requires Python 3.7+

set -euo pipefail

# Colors
INFO='\033[0;36m'; SUCCESS='\033[0;32m'; ERROR='\033[0;31m'; WARN='\033[0;33m'; RESET='\033[0m'

print_info() { echo -e "${INFO}$*${RESET}"; }
print_success() { echo -e "${SUCCESS}$*${RESET}"; }
print_error() { echo -e "${ERROR}$*${RESET}"; }

# Find Python
find_python() {
    for cmd in python3 python; do
        if command -v "$cmd" &> /dev/null; then
            echo "$cmd"
            return 0
        fi
    done
    return 1
}

# Main
main() {
    print_info "\n🔍 SKILL.md Quality Validator (Bash Wrapper)"
    
    if ! python_cmd=$(find_python); then
        print_error "❌ Python 3.7+ not found!"
        exit 1
    fi
    
    script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
    python_script="$script_dir/validate_skill.py"
    
    if [ $# -eq 0 ]; then
        print_error "Usage: $0 <path-to-SKILL.md>"
        exit 1
    fi
    
    skill_path="$1"
    shift
    [ -d "$skill_path" ] && skill_path="$skill_path/SKILL.md"
    
    "$python_cmd" "$python_script" "$skill_path" "$@"
}

main "$@"