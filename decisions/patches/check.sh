#!/bin/bash
# The evidence for the four production hotfixes (m307), re-runnable: each patch alone and all four together, on a
# throwaway worktree of 80a0da3, with the frozen suite each time; the new tests failing on the unpatched code; and
# the Test B pair for 10 fixed people, fingerprinted with and without the patches. It never touches main, a remote
# or a database: everything runs in a temporary folder and a local SQLite file.
#
#   bash decisions/patches/check.sh        (from the repository root, in a Python 3.12 environment with
#                                           brain/requirements-app.txt and pytest installed)
set -u
ROOT=$(git rev-parse --show-toplevel); P="$ROOT/decisions/patches"
W="$(mktemp -d)/frozen"; git -C "$ROOT" worktree add -q --detach "$W" 80a0da3 || exit 1
trap 'git -C "$ROOT" worktree remove --force "$W"' EXIT
NAMES="A1-alert-minimal A2-stored-location A3-log-minimal A4-storage-warning"
reset() { git -C "$W" reset -q && git -C "$W" checkout -q -- . && git -C "$W" clean -fdq; }
suite() { (cd "$W/brain" && python -m pytest -q -p no:cacheprovider tests 2>&1 | tail -n 1); }
apply() { for p in "$@"; do git -C "$W" apply "$P/$p.patch" || { echo "$p DOES NOT APPLY"; return 1; }; done; }
pair() { (cd "$W/brain" && python -I -c "import sys; sys.path.insert(0, 'src'); sys.argv = ['x', '2']; exec(open('$P/testb_same.py').read())" 2>/dev/null | tail -n 1); }

sha256sum "$P"/*.patch
reset; echo "80a0da3 alone: $(suite)"; echo "  Test B pair: $(pair)"
for p in $NAMES; do reset; apply "$p" && echo "$p alone: $(suite)"; done
reset; apply $NAMES && echo "all four: $(suite)" && echo "  Test B pair: $(pair)"
reset; apply A4-storage-warning A3-log-minimal A2-stored-location A1-alert-minimal && echo "all four, reverse order: $(suite)"
for p in $NAMES; do
  t=$(grep -o 'b/brain/tests/test_[a-z_]*\.py' "$P/$p.patch" | head -n 1 | sed 's|^b/||')
  reset; git -C "$W" apply --include="$t" "$P/$p.patch"
  echo "$(basename "$t") on unpatched 80a0da3: $( (cd "$W/brain" && python -m pytest -q -p no:cacheprovider "${t#brain/}" 2>&1 | tail -n 1) )"
done
