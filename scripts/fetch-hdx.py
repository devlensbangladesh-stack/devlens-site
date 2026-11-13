#!/usr/bin/env python3
"""Fetch Bangladesh humanitarian indicators from HDX HAPI into src/data/indicators.json.

Needs the HDX_APP_IDENTIFIER environment variable (free, see
https://hapi.humdata.org/docs, "Generate App Identifier").
An indicator that fails to fetch keeps its previous value, so one bad
response never empties the Data page.
"""
import json, os, sys, urllib.parse, urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE = 'https://hapi.humdata.org/api/v2/'
OUT = Path(__file__).resolve().parent.parent / 'src' / 'data' / 'indicators.json'
APP_ID = os.environ.get('HDX_APP_IDENTIFIER', '').strip()


def fetch(theme, **params):
    """Return every row for a HAPI theme, following pagination."""
    rows, offset, limit = [], 0, 10000
    while True:
        q = urllib.parse.urlencode({**params, 'output_format': 'json', 'limit': limit, 'offset': offset})
        req = urllib.request.Request(BASE + theme + '?' + q, headers={'X-HDX-HAPI-APP-IDENTIFIER': APP_ID})
        with urllib.request.urlopen(req, timeout=60) as r:
            page = json.load(r).get('data', [])
        rows += page
        if len(page) < limit:
            return rows
        offset += limit


def month_year(iso):
    return datetime.fromisoformat(iso[:10]).strftime('%B %Y')


def rohingya_refugees():
    rows = fetch('affected-people/refugees-persons-of-concern',
                 asylum_location_code='BGD', origin_location_code='MMR', population_group='REF')
    if not rows:
        raise ValueError('no refugee rows returned')
    latest = max(r['reference_period_start'] for r in rows)
    rows = [r for r in rows if r['reference_period_start'] == latest]
    totals = [r for r in rows if r.get('gender') == 'all' and r.get('age_range') == 'all']
    if not totals:  # no pre-summed row: add up the gender rows, or everything
        totals = [r for r in rows if r.get('age_range') == 'all' and r.get('gender') != 'all'] or rows
    n = sum(int(r['population']) for r in totals)
    end = rows[0].get('reference_period_end') or latest
    return {
        'id': 'rohingya-refugees',
        'label': 'Refugees from Myanmar in Bangladesh',
        'value': f'{n:,}',
        'period': 'To ' + month_year(end),
        'source': 'UNHCR, via HDX',
        'sourceUrl': 'https://data.humdata.org/dataset/unhcr-population-data-for-world',
    }


def rohingya_appeal():
    rows = [r for r in fetch('coordination-context/funding', location_code='BGD')
            if 'rohingya' in (r.get('appeal_name') or '').lower() and r.get('requirements_usd')]
    if not rows:
        raise ValueError('no Rohingya appeal rows returned')
    r = max(rows, key=lambda x: x['reference_period_start'])
    need, got = float(r['requirements_usd']), float(r.get('funding_usd') or 0)
    return {
        'id': 'rohingya-appeal-funding',
        'label': r['appeal_name'] + ': funding received',
        'value': f'US${got / 1e6:,.0f} million of US${need / 1e6:,.0f} million ({got / need:.0%})',
        'period': r['reference_period_start'][:4],
        'source': 'OCHA Financial Tracking Service, via HDX',
        'sourceUrl': 'https://fts.unocha.org/countries/19/summary/' + r['reference_period_start'][:4],
    }


def main():
    if not APP_ID:
        sys.exit('HDX_APP_IDENTIFIER is not set. Nothing fetched.')
    old = json.loads(OUT.read_text()) if OUT.exists() else {}
    previous = {i['id']: i for i in old.get('indicators', [])}
    indicators, failed = [], 0
    builders = {'rohingya-refugees': rohingya_refugees, 'rohingya-appeal-funding': rohingya_appeal}
    for key, build in builders.items():
        try:
            indicators.append(build())
        except Exception as e:  # keep the last good value
            failed += 1
            print(f'{key}: {e}', file=sys.stderr)
            if key in previous:
                indicators.append(previous[key])
    if indicators == old.get('indicators'):
        print('No change.')
    else:
        OUT.write_text(json.dumps({'fetched': datetime.now(timezone.utc).strftime('%Y-%m-%d'),
                                   'indicators': indicators}, indent=2, ensure_ascii=False) + '\n')
        print(json.dumps(indicators, indent=2, ensure_ascii=False))
    if failed == len(builders):
        sys.exit('Every indicator failed to fetch.')


if __name__ == '__main__':
    main()
