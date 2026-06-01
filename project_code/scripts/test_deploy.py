#!/usr/bin/env python3
"""Smoke-test live Render deployment (frontend, backend, database)."""
import json
import sys
import urllib.error
import urllib.request

BASE = 'https://librarymanagement-main-3.onrender.com'
CHECKS = [
    ('Backend liveness', f'{BASE}/health/', lambda b, c: c == 200 and b.get('status') == 'ok'),
    ('Home redirect', f'{BASE}/', lambda b, c: c in (301, 302, 200)),
    ('Frontend home', f'{BASE}/en/library/', lambda b, c: c == 200 and ('BOOK' in str(b) or 'book' in str(b).lower() or '<html' in str(b))),
    ('Library health', f'{BASE}/en/library/health/?db=1', lambda b, c: c == 200),
    ('Database', f'{BASE}/en/library/test-db/', lambda b, c: isinstance(b, dict) and b.get('status') == 'success'),
]


def fetch(url, timeout=90):
    req = urllib.request.Request(url, headers={'User-Agent': 'bookhub-deploy-test/1.0'})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode('utf-8', errors='replace')
            try:
                data = json.loads(body)
            except json.JSONDecodeError:
                data = body
            return data, resp.status, dict(resp.headers)
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='replace')
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            data = body
        return data, e.code, dict(e.headers)


def main():
    print(f'Testing {BASE}\n')
    failed = 0
    for name, url, ok_fn in CHECKS:
        print(f'— {name}: {url}')
        try:
            body, code, headers = fetch(url)
            routing = headers.get('x-render-routing', headers.get('X-Render-Routing', ''))
            if routing == 'no-server':
                print('  FAIL: Render has no running server (resume/redeploy service)')
                failed += 1
                continue
            if routing == 'suspend':
                print('  FAIL: Render service is suspended')
                failed += 1
                continue
            if ok_fn(body, code):
                print(f'  OK ({code})', json.dumps(body)[:120] if isinstance(body, dict) else '')
            else:
                print(f'  FAIL ({code})', body)
                failed += 1
        except Exception as exc:
            print(f'  FAIL: {exc}')
            failed += 1
        print()
    if failed:
        print(f'{failed} check(s) failed.')
        sys.exit(1)
    print('All checks passed.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
