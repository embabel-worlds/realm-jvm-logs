#!/usr/bin/env python3
"""The battery. See tests/verify.sh for the layers and how to run it."""
import base64, json, os, sys, urllib.request

BASE = os.environ.get('APPLIANCE', 'http://127.0.0.1:8080').rstrip('/')
CREDS = os.environ.get('AUTH') or os.environ.get('EMBABEL_AUTH')
if not CREDS: sys.exit('set AUTH=user:pass')
HERE = os.path.dirname(os.path.abspath(__file__))
TRACE = open(os.path.join(HERE, 'fixtures', 'trace.txt')).read()
EXPECTED = json.load(open(os.path.join(HERE, 'fixtures', 'trace.expected.json')))
NO_JAR = 'jars/no-such-application.jar'

def post(path, body):
    req = urllib.request.Request(BASE + path, data=json.dumps(body).encode(), headers={
        'Content-Type': 'application/json', 'Authorization': 'Basic ' + base64.b64encode(CREDS.encode()).decode()})
    with urllib.request.urlopen(req, timeout=900) as r: return json.loads(r.read().decode())

fails = []
def check(cond, label, detail=''):
    print(('ok   ' if cond else 'FAIL ') + label + (f'  [{detail}]' if detail and not cond else ''), flush=True)
    if not cond: fails.append(label)

def view(name, args=None):
    try:
        d = post(f'/api/v1/admin/kg/views/{name}/run', {'args': args or {}})
    except Exception as e:
        check(False, f'L1 {name} answers', str(e)[:300]); return None
    err = d.get('error')
    check(not err, f'L1 {name} answers', str(err)[:300])
    return d.get('rows') or []

# ---- L1: every view by name --------------------------------------------------------------------
for name in ('JvmLogFailures', 'JvmLogFailureCode', 'JvmLogLevels', 'JvmFailureCallers',
             'JvmFailureLocals', 'JvmFailingMethodShape'):
    view(name)
view('JvmThrowSiteCoverage', {'jar': NO_JAR})
rows = view('JvmUnseenThrowSites', {'jar': NO_JAR, 'exception': 'java.lang.IllegalStateException'})
if rows is not None:
    check(rows == [], 'L1 JvmUnseenThrowSites on a jar that is not there answers nothing', rows[:2])

# ---- L2: the fixture trace, exactly --------------------------------------------------------------
rows = view('JvmStackTraceSummary', {'trace': TRACE})
if rows is not None:
    keys = list(EXPECTED[0])
    got = [{k: (bool(r.get(k)) if k == 'rootCause' else r.get(k)) for k in keys} for r in rows]
    check(len(got) == len(EXPECTED), 'L2 JvmStackTraceSummary: one row per throwable', f'{len(got)} vs {len(EXPECTED)}')
    for want, have in zip(EXPECTED, got):
        for k in keys:
            check(have[k] == want[k], f"L2 throwable {want['index']} {k} = {want[k]!r}", repr(have[k]))
rows = view('JvmStackTraceCode', {'trace': TRACE})
if rows is not None:
    # No jar under data/jars compiled com.acme.shop, so no frame is in a jar and the view keeps none.
    check(rows == [], 'L2 JvmStackTraceCode keeps only frames in a jar: none here', rows[:2])

print(f'{len(fails)} failure(s)' if fails else 'ALL CHECKS PASS', flush=True)
sys.exit(1 if fails else 0)
