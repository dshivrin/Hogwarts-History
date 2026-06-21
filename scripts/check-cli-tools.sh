#!/usr/bin/env bash

set -u

missing_required=()
missing_recommended=()
missing_optional=()

check_tool() {
  local cmd="$1"
  local label="$2"
  local level="$3"

  printf "%-10s %-13s " "$cmd" "[$level]"

  if command -v "$cmd" >/dev/null 2>&1; then
    printf "FOUND  "

    case "$cmd" in
      rg)
        rg --version | head -n 1
        ;;
      jq)
        jq --version
        ;;
      yq)
        yq --version | head -n 1
        ;;
      just)
        just --version
        ;;
      make)
        make --version | head -n 1
        ;;
      *)
        command -v "$cmd"
        ;;
    esac
  else
    echo "MISSING - $label"

    case "$level" in
      required)
        missing_required+=("$cmd")
        ;;
      recommended)
        missing_recommended+=("$cmd")
        ;;
      optional)
        missing_optional+=("$cmd")
        ;;
    esac
  fi
}

echo "Checking CLI tools..."
echo

check_tool "rg"   "fast repo search / ripgrep" "required"
check_tool "jq"   "JSON inspection"            "recommended"
check_tool "just" "project command runner"     "recommended"
check_tool "yq"   "YAML inspection"            "optional"
check_tool "make" "fallback command runner"    "optional"

echo

if command -v brew >/dev/null 2>&1; then
  install_list=()

  for tool in "${missing_required[@]}" "${missing_recommended[@]}" "${missing_optional[@]}"; do
    case "$tool" in
      rg)
        install_list+=("ripgrep")
        ;;
      jq)
        install_list+=("jq")
        ;;
      yq)
        install_list+=("yq")
        ;;
      just)
        install_list+=("just")
        ;;
      make)
        # macOS already ships make; do not suggest brew install by default.
        ;;
    esac
  done

  if [ "${#install_list[@]}" -gt 0 ]; then
    echo "Suggested Homebrew install command:"
    echo "brew install ${install_list[*]}"
    echo
  fi
else
  echo "Homebrew not found. Skipping install suggestion."
  echo
fi

if [ "${#missing_required[@]}" -gt 0 ]; then
  echo "Result: missing required tools: ${missing_required[*]}"
  exit 1
fi

echo "Result: required tools are available."
exit 0