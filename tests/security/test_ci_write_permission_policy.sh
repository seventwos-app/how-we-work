#!/usr/bin/env bash
# Regression for ci.yml's "security" job write-permission policy: a
# trusted allowlist (graphify.yml, graphify-catchup.yml) may request
# write permissions only because they are separately proven to have no
# pull_request/pull_request_target trigger; every other workflow must
# stay read-only. This mirrors the inline shell logic in
# .github/workflows/ci.yml exactly, against fixture workflow files in a
# throwaway directory, so a change to one can be checked against the
# other without needing to run this repo's real workflows in CI.
set -euo pipefail

workdir="$(mktemp -d)"
trap 'rm -rf "${workdir}"' EXIT
mkdir -p "${workdir}/.github/workflows"
cd "${workdir}"

write_fixture() {
  # write_fixture <path> <heredoc content via stdin>
  cat > "$1"
}

check_pull_request_target() {
  ! grep -rnE '^[[:space:]]*pull_request_target:' .github/workflows
}

check_trusted_have_no_pr_trigger() {
  local trusted="graphify.yml graphify-catchup.yml"
  for f in $trusted; do
    local path=".github/workflows/$f"
    [ -f "$path" ] || return 1
    if grep -nE '^[[:space:]]*pull_request(_target)?:' "$path"; then
      return 1
    fi
  done
  return 0
}

check_other_workflows_read_only() {
  local trusted="./.github/workflows/graphify.yml ./.github/workflows/graphify-catchup.yml"
  local fail=0
  for f in .github/workflows/*.yml .github/workflows/*.yaml; do
    [ -f "$f" ] || continue
    local skip=0
    for t in $trusted; do
      if [ "./$f" = "$t" ]; then
        skip=1
      fi
    done
    if [ "$skip" -eq 1 ]; then
      continue
    fi
    if grep -nE '^[[:space:]]*(contents|issues|pull-requests|packages|id-token):[[:space:]]*(write|write-all)' "$f" \
      || grep -nE '^[[:space:]]*permissions:[[:space:]]*write-all' "$f"; then
      fail=1
    fi
  done
  [ "$fail" -eq 0 ]
}

fails=0
expect() {
  local description="$1"
  local expected="$2" # "pass" or "fail"
  local actual="fail"
  if "$3"; then
    actual="pass"
  fi
  if [ "$actual" = "$expected" ]; then
    echo "PASS: ${description}"
  else
    echo "FAIL: ${description} (expected ${expected}, got ${actual})"
    fails=1
  fi
}

# --- Case 1: real-shaped trusted graphify workflows (push/schedule only,
#     write permissions) plus a read-only CI workflow -- everything
#     should pass, matching this repo's actual configuration. ---
rm -rf .github/workflows && mkdir -p .github/workflows
write_fixture .github/workflows/graphify.yml <<'EOF'
on:
  push:
    branches: [main]
permissions:
  contents: write
  pull-requests: write
EOF
write_fixture .github/workflows/graphify-catchup.yml <<'EOF'
on:
  schedule:
    - cron: '17 3 * * *'
permissions:
  contents: write
  pull-requests: write
EOF
write_fixture .github/workflows/ci.yml <<'EOF'
on:
  pull_request:
permissions:
  contents: read
EOF
expect "no pull_request_target anywhere (baseline)" pass check_pull_request_target
expect "trusted graphify workflows have no pull_request trigger (baseline)" pass check_trusted_have_no_pr_trigger
expect "non-trusted workflows are read-only (baseline)" pass check_other_workflows_read_only

# --- Case 2: an untrusted workflow requests write permissions -- must
#     fail the read-only scan. ---
write_fixture .github/workflows/malicious.yml <<'EOF'
on:
  pull_request:
permissions:
  contents: write
EOF
expect "untrusted workflow requesting write permissions is rejected" fail check_other_workflows_read_only

# --- Case 3: a permissions: write-all shorthand on an untrusted workflow
#     must also be rejected. ---
rm -f .github/workflows/malicious.yml
write_fixture .github/workflows/malicious.yml <<'EOF'
on:
  pull_request:
permissions: write-all
EOF
expect "untrusted workflow using permissions: write-all is rejected" fail check_other_workflows_read_only
rm -f .github/workflows/malicious.yml

# --- Case 4: if a trusted-named file were changed to add a
#     pull_request/pull_request_target trigger, the trust assertion must
#     fail closed rather than silently keep trusting its write
#     permissions. ---
write_fixture .github/workflows/graphify.yml <<'EOF'
on:
  push:
    branches: [main]
  pull_request:
permissions:
  contents: write
  pull-requests: write
EOF
expect "trusted workflow gaining a pull_request trigger is rejected" fail check_trusted_have_no_pr_trigger

write_fixture .github/workflows/graphify.yml <<'EOF'
on:
  pull_request_target:
permissions:
  contents: write
EOF
expect "trusted workflow gaining a pull_request_target trigger is rejected" fail check_trusted_have_no_pr_trigger
expect "pull_request_target scan still catches it repo-wide" fail check_pull_request_target

if [ "$fails" -ne 0 ]; then
  echo "One or more write-permission policy regressions failed." >&2
  exit 1
fi
echo "All write-permission policy regressions passed."
