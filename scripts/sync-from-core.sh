#!/usr/bin/env bash
# Copy the daikin integration out of a Home Assistant core release into
# custom_components/daikin, then report what this repo changed on top of it.
#
#   scripts/sync-from-core.sh 2026.9.3
#
# Run it on a clean tree: the copy overwrites custom_components/daikin, and
# `git diff` afterwards is exactly this repo's delta against that core release.
set -euo pipefail

TAG="${1:?usage: sync-from-core.sh <home-assistant core tag, e.g. 2026.9.3>}"
REPO_ROOT="$(git -C "$(dirname "$0")" rev-parse --show-toplevel)"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

git clone -q --depth 1 --filter=blob:none --sparse \
    --branch "$TAG" https://github.com/home-assistant/core "$WORK/core"
git -C "$WORK/core" sparse-checkout set homeassistant/components/daikin >/dev/null

echo "core $TAG is commit $(git -C "$WORK/core" rev-parse HEAD)"

rm -rf "$REPO_ROOT/custom_components/daikin"
mkdir -p "$REPO_ROOT/custom_components/daikin"
cp "$WORK/core/homeassistant/components/daikin/"* "$REPO_ROOT/custom_components/daikin/"

echo "copied; this repo's delta against core $TAG:"
git -C "$REPO_ROOT" --no-pager diff --stat -- custom_components/daikin
