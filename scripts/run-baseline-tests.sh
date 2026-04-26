#!/usr/bin/env bash
set -euo pipefail

python3 -m pytest tests/security tests/baseline tests/rendering tests/validation
