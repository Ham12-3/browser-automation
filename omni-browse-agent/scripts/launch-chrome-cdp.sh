#!/usr/bin/env bash
set -euo pipefail
PORT="${OMNI_CDP_PORT:-9222}"
PROFILE="${TMPDIR:-/tmp}/omnibrowse-chrome-cdp"
if command -v google-chrome >/dev/null 2>&1; then
  google-chrome --remote-debugging-port="$PORT" --user-data-dir="$PROFILE" about:blank &
elif command -v chromium >/dev/null 2>&1; then
  chromium --remote-debugging-port="$PORT" --user-data-dir="$PROFILE" about:blank &
elif command -v open >/dev/null 2>&1; then
  open -na "Google Chrome" --args --remote-debugging-port="$PORT" --user-data-dir="$PROFILE" about:blank
else
  echo "Could not find Chrome/Chromium launcher." >&2
  exit 1
fi
echo "Chromium browser launched with CDP at http://127.0.0.1:$PORT"

