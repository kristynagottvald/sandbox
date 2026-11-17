#!/usr/bin/env bash
# Poll a live URL until its body contains a marker string (a line you just added), then report. Do not use sleep loops by hand.
#   wait-live.sh https://kristynagottvald.github.io/sandbox/<app>/ 'some new string' [timeout_seconds=180]
URL="${1:?url}"; MARK="${2:?marker string}"; T="${3:-180}"; END=$((SECONDS+T))
while [ $SECONDS -lt $END ]; do
  if curl -s "$URL" | grep -qF -- "$MARK"; then echo "LIVE: $URL contains '$MARK'"; exit 0; fi
  sleep 4
done
echo "NOT LIVE after ${T}s: $URL does not contain '$MARK' (check the Pages deploy run)"; exit 1
