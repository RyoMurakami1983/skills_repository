#!/usr/bin/env bash
# Deploy Python skills from skills_repository to a target project.

set -euo pipefail

readonly SCRIPT_NAME="$(basename "$0")"
readonly DEV_ENV_SKILLS=("python-setup-dev-environment")

SOURCE_ROOT=""
TARGET=""
CATEGORY=""
LIST_MODE=0
FORCE=0
WHAT_IF=0
declare -a REQUESTED_SKILLS=()

usage() {
    cat <<EOF
Usage:
  $SCRIPT_NAME --source-root <path> --list
  $SCRIPT_NAME --source-root <path> --target <project> --category <dev-env|all> [--what-if] [--force]
  $SCRIPT_NAME --source-root <path> --target <project> --skills <skill1,skill2> [--what-if] [--force]

Options:
  --source-root <path>   Path to the python/ source directory
  --target <path>        Path to the target project root
  --category <name>      Category name: dev-env or all
  --skills <csv>         Comma-separated skill names
  --list                 Show available categories and skills, then exit
  --force                Overwrite existing copied skills
  --what-if              Preview actions without copying files
  -h, --help             Show this help text
EOF
}

join_by() {
    local delimiter="$1"
    shift
    local first=1
    for item in "$@"; do
        if [[ $first -eq 1 ]]; then
            printf '%s' "$item"
            first=0
        else
            printf '%s%s' "$delimiter" "$item"
        fi
    done
}

parse_args() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --source-root)
                if [[ $# -lt 2 || "$2" == --* ]]; then
                    echo "--source-root requires a value." >&2
                    usage >&2
                    exit 1
                fi
                SOURCE_ROOT="$2"
                shift 2
                ;;
            --target)
                if [[ $# -lt 2 || "$2" == --* ]]; then
                    echo "--target requires a value." >&2
                    usage >&2
                    exit 1
                fi
                TARGET="$2"
                shift 2
                ;;
            --category)
                if [[ $# -lt 2 || "$2" == --* ]]; then
                    echo "--category requires a value." >&2
                    usage >&2
                    exit 1
                fi
                CATEGORY="$2"
                shift 2
                ;;
            --skills)
                if [[ $# -lt 2 || "$2" == --* ]]; then
                    echo "--skills requires a value." >&2
                    usage >&2
                    exit 1
                fi
                local IFS=','
                read -r -a parsed <<< "$2"
                local trimmed_parsed=()
                for skill in "${parsed[@]}"; do
                    skill="${skill#"${skill%%[![:space:]]*}"}"
                    skill="${skill%"${skill##*[![:space:]]}"}"
                    trimmed_parsed+=("$skill")
                done
                REQUESTED_SKILLS+=("${trimmed_parsed[@]}")
                shift 2
                ;;
            --list)
                LIST_MODE=1
                shift
                ;;
            --force)
                FORCE=1
                shift
                ;;
            --what-if)
                WHAT_IF=1
                shift
                ;;
            -h|--help)
                usage
                exit 0
                ;;
            *)
                echo "Unknown argument: $1" >&2
                usage >&2
                exit 1
                ;;
        esac
    done
}

get_available_skills() {
    find "$SOURCE_ROOT" -mindepth 1 -maxdepth 1 -type d | while IFS= read -r dir; do
        if [[ -f "$dir/SKILL.md" ]]; then
            basename "$dir"
        fi
    done | sort
}

resolve_category_skills() {
    case "$1" in
        dev-env)
            printf '%s\n' "${DEV_ENV_SKILLS[@]}"
            ;;
        all)
            printf '%s\n' "${AVAILABLE_SKILLS[@]}"
            ;;
        *)
            echo "Unsupported category: $1" >&2
            exit 1
            ;;
    esac
}

contains_skill() {
    local needle="$1"
    shift
    for item in "$@"; do
        if [[ "$item" == "$needle" ]]; then
            return 0
        fi
    done
    return 1
}

print_list() {
    echo
    echo "=== Available Python Skill Categories ==="
    echo

    local categories=("dev-env" "all")
    for category_name in "${categories[@]}"; do
        mapfile -t category_skills < <(resolve_category_skills "$category_name")
        local label="$category_name"
        case "$category_name" in
            dev-env) label="Development Environment Foundation" ;;
            all) label="All Available Python Skills" ;;
        esac
        echo "  $category_name (${#category_skills[@]} skills) - $label"
        for skill_name in "${category_skills[@]}"; do
            echo "    [ok] $skill_name"
        done
        echo
    done

    echo "=== Available Individual Python Skills ==="
    for skill_name in "${AVAILABLE_SKILLS[@]}"; do
        echo "  - $skill_name"
    done
    echo
    echo "Total available: ${#AVAILABLE_SKILLS[@]} skills"
    echo
}

deploy_skills() {
    local dest_base="$TARGET/.github/skills"
    local -a copied=()
    local -a overwritten=()
    local -a skipped=()

    for skill_name in "${TARGET_SKILLS[@]}"; do
        local src_path="$SOURCE_ROOT/$skill_name"
        local dest_path="$dest_base/$skill_name"
        if [[ -d "$dest_path" && $FORCE -eq 0 ]]; then
            skipped+=("$skill_name")
            if [[ $WHAT_IF -eq 1 ]]; then
                echo "  SKIP  $skill_name (already exists, use --force to overwrite)"
            fi
            continue
        fi

        if [[ $WHAT_IF -eq 1 ]]; then
            if [[ -d "$dest_path" ]]; then
                overwritten+=("$skill_name")
                echo "  OVERWRITE  $skill_name -> $dest_path"
            else
                copied+=("$skill_name")
                echo "  COPY  $skill_name -> $dest_path"
            fi
            continue
        fi

        mkdir -p "$dest_base"
        if [[ -d "$dest_path" ]]; then
            rm -rf "$dest_path"
            overwritten+=("$skill_name")
        else
            copied+=("$skill_name")
        fi
        cp -R "$src_path" "$dest_path"
    done

    echo
    echo "=== Deploy Summary ==="
    echo "  Source:  $SOURCE_ROOT"
    echo "  Target:  $dest_base"
    if [[ -n "$CATEGORY" ]]; then
        echo "  Category: $CATEGORY"
    fi
    echo

    if [[ ${#copied[@]} -gt 0 ]]; then
        echo "  Copied (${#copied[@]}):"
        for skill_name in "${copied[@]}"; do
            echo "    + $skill_name"
        done
    fi

    if [[ ${#overwritten[@]} -gt 0 ]]; then
        echo "  Overwritten (${#overwritten[@]}):"
        for skill_name in "${overwritten[@]}"; do
            echo "    ~ $skill_name"
        done
    fi

    if [[ ${#skipped[@]} -gt 0 ]]; then
        echo "  Skipped (${#skipped[@]}):"
        for skill_name in "${skipped[@]}"; do
            echo "    - $skill_name (already exists)"
        done
    fi

    local total_actions=$(( ${#copied[@]} + ${#overwritten[@]} ))
    echo
    echo "  Total deployed: $total_actions skill(s)"
    if [[ $WHAT_IF -eq 1 ]]; then
        echo "  (Dry run - no files were copied)"
    fi
    echo
}

parse_args "$@"

if [[ -z "$SOURCE_ROOT" ]]; then
    echo "--source-root is required." >&2
    usage >&2
    exit 1
fi

if [[ ! -d "$SOURCE_ROOT" ]]; then
    echo "--source-root directory not found: $SOURCE_ROOT" >&2
    exit 1
fi

mapfile -t AVAILABLE_SKILLS < <(get_available_skills)

if [[ $LIST_MODE -eq 1 ]]; then
    print_list
    exit 0
fi

if [[ -z "$TARGET" ]]; then
    echo "Target is required when not using --list. Specify --target <project-path>." >&2
    exit 1
fi

if [[ -z "$CATEGORY" && ${#REQUESTED_SKILLS[@]} -eq 0 ]]; then
    echo "Specify --category or --skills to select which skills to deploy." >&2
    exit 1
fi

declare -a TARGET_SKILLS=()
if [[ -n "$CATEGORY" ]]; then
    mapfile -t TARGET_SKILLS < <(resolve_category_skills "$CATEGORY")
fi

if [[ ${#REQUESTED_SKILLS[@]} -gt 0 ]]; then
    TARGET_SKILLS+=("${REQUESTED_SKILLS[@]}")
fi

if [[ ${#TARGET_SKILLS[@]} -eq 0 ]]; then
    echo "No skills selected for deployment." >&2
    exit 1
fi

mapfile -t TARGET_SKILLS < <(printf '%s\n' "${TARGET_SKILLS[@]}" | awk 'NF {print}' | sort -u)

declare -a INVALID_SKILLS=()
for skill_name in "${TARGET_SKILLS[@]}"; do
    if ! contains_skill "$skill_name" "${AVAILABLE_SKILLS[@]}"; then
        INVALID_SKILLS+=("$skill_name")
    fi
done

if [[ ${#INVALID_SKILLS[@]} -gt 0 ]]; then
    echo "Skills not found in source: $(join_by ', ' "${INVALID_SKILLS[@]}")" >&2
    exit 1
fi

deploy_skills
