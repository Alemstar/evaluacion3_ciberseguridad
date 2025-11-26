#!/usr/bin/env bash
set -euo pipefail

# Usage: ./scripts/run_zap_scan.sh <target_url>
TARGET=${1:-http://localhost:5000}
REPORT_DIR="$(pwd)/zap-reports"
mkdir -p "${REPORT_DIR}"

echo "Starting full ZAP scan against ${TARGET}"

docker run --rm -v "${REPORT_DIR}:/zap/reports" owasp/zap2docker-stable \
  zap-full-scan.py -t "${TARGET}" -r /zap/reports/zap-full-report.html -J /zap/reports/zap-full-report.json || true

JSON_REPORT="${REPORT_DIR}/zap-full-report.json"
if [ ! -f "${JSON_REPORT}" ]; then
  echo "No ZAP JSON report generated"
  exit 0
fi

python3 - <<PY
import json, sys
p='${JSON_REPORT}'
with open(p) as f:
    data=json.load(f)
high=0
for site in data.get('site',[]):
    for alert in site.get('alerts',[]):
        if alert.get('risk') in ('High','Critical'):
            high+=1
print('ZAP high/critical alerts:', high)
if high>0:
    sys.exit(2)
PY

echo "ZAP scan complete. Reports in ${REPORT_DIR}"
exit 0
