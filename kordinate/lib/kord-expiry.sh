#!/bin/bash
# Generic two-stage kord cache expiry.
# Usage: kord-expiry.sh <kord-dir>
# Exit 0 = fresh, 1 = stale, 2 = uncertain
#
# Reads cache_inputs from contract.md frontmatter.
# Computes staleness from change magnitude + age decay.

set -euo pipefail

KORD_DIR="${1:-.}"
KORDINATE_HOME="${KORDINATE_HOME:-$HOME/.kord}"
CONTRACT="$KORD_DIR/contract.md"
DATA="$KORD_DIR/data.md"
SNAPSHOT="$KORD_DIR/.snapshot"

# No cached data -> stale
[ -s "$DATA" ] || exit 1

# No contract -> stale
[ -f "$CONTRACT" ] || exit 1

# Parse cache_inputs from contract frontmatter.
# Extracts: paths[], threshold, stale_threshold, max_age.
read_config() {
  python3 -c "
import sys, re

content = open(sys.argv[1]).read()
fm = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
if not fm:
    sys.exit(1)

block = fm.group(1)
if 'cache_inputs:' not in block:
    sys.exit(1)

# Collect paths
paths = []
in_paths = False
for line in block.split('\n'):
    s = line.strip()
    if s == 'paths:':
        in_paths = True
        continue
    if in_paths:
        if s.startswith('- '):
            paths.append(s[2:].strip())
        elif s and not s.startswith('-'):
            in_paths = False

if not paths:
    sys.exit(1)

# Scalar values with defaults
threshold = 0.05
stale_threshold = 0.30
max_age_days = 7

for line in block.split('\n'):
    s = line.strip()
    if s.startswith('threshold:') and 'stale' not in s:
        try: threshold = float(s.split(':',1)[1].strip())
        except: pass
    elif s.startswith('stale_threshold:'):
        try: stale_threshold = float(s.split(':',1)[1].strip())
        except: pass
    elif s.startswith('max_age:'):
        val = s.split(':',1)[1].strip()
        m = re.match(r'(\d+)d', val)
        if m:
            max_age_days = int(m.group(1))

home = sys.argv[2]
resolved = ' '.join(home + '/' + p for p in paths)
print(f'CACHE_PATHS=\"{resolved}\"')
print(f'THRESHOLD={threshold}')
print(f'STALE_THRESHOLD={stale_threshold}')
print(f'MAX_AGE_DAYS={max_age_days}')
" "$CONTRACT" "$KORDINATE_HOME" 2>/dev/null
}

CONFIG="$(read_config)" || exit 1
eval "$CONFIG"

# No paths parsed -> stale
[ -n "${CACHE_PATHS:-}" ] || exit 1

# -- Age computation --

DATA_MTIME=$(stat -c %Y "$DATA" 2>/dev/null || stat -f %m "$DATA" 2>/dev/null || echo 0)
NOW=$(date +%s)
AGE_SECONDS=$((NOW - DATA_MTIME))

# Max age exceeded -> stale
MAX_AGE_SECONDS=$((MAX_AGE_DAYS * 86400))
[ "$AGE_SECONDS" -lt "$MAX_AGE_SECONDS" ] || exit 1

# -- Change magnitude --

# No snapshot -> uncertain (we have data but cannot measure change)
[ -f "$SNAPSHOT" ] || exit 2

# Count total lines across input paths (config-relevant file types)
TOTAL_LINES=0
for path in $CACHE_PATHS; do
  if [ -d "$path" ]; then
    count=$(find "$path" -type f \( -name "*.md" -o -name "*.yaml" -o -name "*.yml" \
      -o -name "*.json" -o -name "*.sh" -o -name "*.js" \) 2>/dev/null \
      | xargs wc -l 2>/dev/null | tail -1 | awk '{print $1}')
    TOTAL_LINES=$((TOTAL_LINES + ${count:-0}))
  elif [ -f "$path" ]; then
    count=$(wc -l < "$path" 2>/dev/null || echo 0)
    TOTAL_LINES=$((TOTAL_LINES + count))
  fi
done

# Measure changed lines against snapshot
CHANGED_LINES=0
while IFS= read -r line; do
  [ -n "$line" ] || continue
  old_count=$(echo "$line" | awk '{print $1}')
  old_hash=$(echo "$line" | awk '{print $2}')
  old_path=$(echo "$line" | awk '{$1=$2=""; sub(/^ +/, ""); print}')

  if [ -f "$old_path" ]; then
    new_hash=$(md5sum "$old_path" 2>/dev/null | cut -d' ' -f1)
    if [ "$old_hash" != "$new_hash" ]; then
      new_count=$(wc -l < "$old_path" 2>/dev/null || echo 0)
      diff_lines=$(( new_count > old_count ? new_count - old_count : old_count - new_count ))
      # Hash differs but line count unchanged -> at least 1 line changed
      [ "$diff_lines" -gt 0 ] || diff_lines=1
      CHANGED_LINES=$((CHANGED_LINES + diff_lines))
    fi
  else
    # File deleted -> all its lines count as changed
    CHANGED_LINES=$((CHANGED_LINES + old_count))
  fi
done < "$SNAPSHOT"

# Detect new files not in snapshot
for path in $CACHE_PATHS; do
  if [ -d "$path" ]; then
    while IFS= read -r f; do
      [ -n "$f" ] || continue
      if ! grep -qF "$f" "$SNAPSHOT" 2>/dev/null; then
        new_lines=$(wc -l < "$f" 2>/dev/null || echo 0)
        CHANGED_LINES=$((CHANGED_LINES + new_lines))
      fi
    done < <(find "$path" -type f \( -name "*.md" -o -name "*.yaml" -o -name "*.yml" \
      -o -name "*.json" -o -name "*.sh" -o -name "*.js" \) 2>/dev/null)
  elif [ -f "$path" ]; then
    if ! grep -qF "$path" "$SNAPSHOT" 2>/dev/null; then
      new_lines=$(wc -l < "$path" 2>/dev/null || echo 0)
      CHANGED_LINES=$((CHANGED_LINES + new_lines))
    fi
  fi
done

[ "$TOTAL_LINES" -gt 0 ] || TOTAL_LINES=1

# -- Staleness score: change_ratio + (age_ratio * change_ratio) --

RESULT=$(python3 -c "
change_ratio = $CHANGED_LINES / $TOTAL_LINES
age_ratio = min($AGE_SECONDS / ($MAX_AGE_DAYS * 86400), 1.0)
score = change_ratio + (age_ratio * change_ratio)

if score < $THRESHOLD:
    print('fresh')
elif score > $STALE_THRESHOLD:
    print('stale')
else:
    print('uncertain')
")

case "$RESULT" in
  fresh) exit 0 ;;
  stale) exit 1 ;;
  *)     exit 2 ;;
esac
