#!/usr/bin/env bash
set -euo pipefail

usage(){ echo "Usage: $0 {dns|tcp|http|route} TARGET [PORT]" >&2; exit 64; }
[[ $# -ge 2 ]] || usage
MODE="$1"; TARGET="$2"; PORT="${3:-443}"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
SAFE_TARGET="$(printf '%s' "$TARGET" | tr -cd '[:alnum:]._:/?=&%-')"
[[ -n "$SAFE_TARGET" ]] || { echo "Target contains no safe characters" >&2; exit 65; }
EVIDENCE_DIR="${EVIDENCE_DIR:-evidence}"
mkdir -p "$EVIDENCE_DIR"
OUTPUT="$EVIDENCE_DIR/${STAMP}-${MODE}.txt"

{
  echo "Cloud Support Operations Lab"
  echo "timestamp=$STAMP"
  echo "mode=$MODE"
  echo "target_hint=${SAFE_TARGET:0:3}***"
  echo "---"
  case "$MODE" in
    dns)
      if command -v dig >/dev/null; then dig +time=3 +tries=1 "$SAFE_TARGET" A; else nslookup "$SAFE_TARGET"; fi
      ;;
    tcp)
      nc -vz -w 5 "$SAFE_TARGET" "$PORT"
      ;;
    http)
      [[ "$SAFE_TARGET" == http://* || "$SAFE_TARGET" == https://* ]] || { echo "HTTP mode requires an http(s) URL"; exit 65; }
      curl --fail --silent --show-error --location --max-time 10 --output /dev/null --write-out 'status=%{http_code}\ntime_total=%{time_total}\nremote_ip=[redacted]\n' "$SAFE_TARGET"
      ;;
    route)
      if command -v traceroute >/dev/null; then traceroute -m 12 "$SAFE_TARGET"; else route get "$SAFE_TARGET"; fi
      ;;
    *) usage ;;
  esac
} 2>&1 | sed -E 's/([0-9]{1,3}\.){3}[0-9]{1,3}/[ip-redacted]/g' | tee "$OUTPUT"

if command -v shasum >/dev/null; then shasum -a 256 "$OUTPUT" >"$OUTPUT.sha256"; else sha256sum "$OUTPUT" >"$OUTPUT.sha256"; fi
echo "Evidence saved to $OUTPUT"
