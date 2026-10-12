#!/usr/bin/env bash
set -euo pipefail

# SteadyCraft Build Automation Script Wrapper
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "${SCRIPT_DIR}/build.py" "$@"
