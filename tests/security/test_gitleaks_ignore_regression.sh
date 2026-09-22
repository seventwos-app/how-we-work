#!/usr/bin/env bash
# End-to-end regression proving a PR-committed .gitleaksignore cannot
# suppress a known secret when gitleaks is invoked the way
# .github/workflows/security-canary.yml invokes it (pinned --config,
# pinned empty --gitleaks-ignore-path, and removal of any working-tree
# .gitleaksignore/.gitleaks.toml before the scan).
#
# gitleaks always additionally looks up "./.gitleaksignore" relative to
# the scanned source path even when --gitleaks-ignore-path points
# elsewhere, so a pull request that commits its own .gitleaksignore
# (naming the fingerprint of a real secret it also introduces) could
# otherwise suppress that finding. This script proves: (a) the
# suppression is real when the workflow's mitigation step is skipped,
# and (b) it is closed when that step runs, using the exact commands the
# workflow runs.
#
# Requires network access (to fetch the pinned gitleaks config) and the
# gitleaks CLI on PATH. Skips (exit 0) if either is unavailable, since
# this is a defense-in-depth regression run as part of the manual
# validation gate, not a required CI check.
set -euo pipefail

if ! command -v gitleaks >/dev/null 2>&1; then
  echo "SKIP: gitleaks CLI not found on PATH"
  exit 0
fi

workdir="$(mktemp -d)"
trap 'rm -rf "${workdir}"' EXIT

repo="${workdir}/repo"
mkdir -p "${repo}"
cd "${repo}"
git init -q
git config user.email "test@example.com"
git config user.name "test"

# A known-detectable secret (gitleaks' built-in "github-pat" rule).
# Assembled at runtime from two fragments, using variable names that
# avoid gitleaks' generic-api-key keyword list, so this script's own
# source bytes never contain (a) the contiguous ghp_[0-9a-zA-Z]{36}
# pattern, or (b) a keyword+"="+high-entropy-value pair that would
# itself look like a secret in this script's own source. Only the
# throwaway repo's committed file content is the contiguous, matchable
# secret this regression needs gitleaks to detect.
fragment_a="ghp_1234567890abcdefghij1234567890abc"
fragment_b="def"
echo "GITHUB_TOKEN=${fragment_a}${fragment_b}" > secret.txt
git add secret.txt
git commit -q -m "add secret"

leak_commit="$(git rev-parse HEAD)"
fingerprint="${leak_commit}:secret.txt:github-pat:1"

echo "${fingerprint}" > .gitleaksignore
git add .gitleaksignore
git commit -q -m "add gitleaksignore suppressing the secret"

# Pin gitleaks' own default ruleset, exactly as the workflow does.
config_commit="83d9cd684c87d95d656c1458ef04895a7f1cbd8e"
config_checksum="e163e53b9e7e8a8511e77271e2b323ed057759542a6d988258afe3a1fa329caf"
config_path="${workdir}/gitleaks.toml"
if ! curl -fsSL -o "${config_path}" \
  "https://raw.githubusercontent.com/gitleaks/gitleaks/${config_commit}/config/gitleaks.toml"; then
  echo "SKIP: unable to fetch pinned gitleaks config (no network access)"
  exit 0
fi
echo "${config_checksum}  ${config_path}" | sha256sum -c -
ignore_dir="${workdir}/empty-ignore-dir"
mkdir -p "${ignore_dir}"

run_gitleaks() {
  set +e
  gitleaks git --redact --no-banner --exit-code 1 \
    --config "${config_path}" \
    --gitleaks-ignore-path "${ignore_dir}" \
    --ignore-gitleaks-allow \
    . >/dev/null 2>&1
  echo $?
}

# 1. Prove the bypass exists when the mitigation step is skipped: the
#    working-tree .gitleaksignore is still honored even though --config
#    and --gitleaks-ignore-path both point at trusted, pinned locations.
exit_code_with_bypass="$(run_gitleaks)"
if [ "${exit_code_with_bypass}" != "0" ]; then
  echo "FAIL: expected the unmitigated scan to be suppressed (exit 0) by the working-tree .gitleaksignore, got ${exit_code_with_bypass}"
  exit 1
fi
echo "confirmed: an unmitigated scan is suppressed by a PR-controlled .gitleaksignore (exit ${exit_code_with_bypass})"

# 2. Apply the workflow's mitigation (remove the working-tree ignore
#    file) and prove the same known secret is now detected.
rm -f .gitleaksignore .gitleaks.toml
exit_code_mitigated="$(run_gitleaks)"
if [ "${exit_code_mitigated}" != "1" ]; then
  echo "FAIL: expected the mitigated scan to detect the known secret (exit 1), got ${exit_code_mitigated}"
  exit 1
fi

echo "PASS: removing the working-tree .gitleaksignore before scanning restores detection of a known secret (exit ${exit_code_mitigated})."
