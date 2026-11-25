#!/bin/sh
# Ground-truth battery for realm-jvm-logs.
#   L1 every view answers by name, on its defaults (the log views over whatever data/logs holds,
#      which may be nothing) and on the fixture trace below
#   L2 a pasted stack trace read back exactly: tests/fixtures/trace.txt is written by hand, so every
#      throwable's relation, depth, parent, message, root cause, frame count and elision is known
#      without the appliance (tests/fixtures/trace.expected.json)
#   L3 none: this realm declares no pushdown of its own; the files kind filters as it walks
#
#   APPLIANCE=http://127.0.0.1:8080 AUTH=user:pass sh tests/verify.sh
# (EMBABEL_AUTH=user:pass is accepted in place of AUTH.) No source keys are needed.
# The last line on success is exactly `ALL CHECKS PASS`; any failure exits non-zero.
set -e
cd "$(dirname "$0")/.."
exec python3 tests/verify.py "$@"
