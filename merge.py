#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Merge the daily files into one table. Standard library only.

    python3 merge.py                        everything, to stdout
    python3 merge.py --zone CZ --from 2024-01-01 > cz.csv
    python3 merge.py --zone DE-LU --resolution 60 --from 2025-01-01

The data is stored one file per delivery day so that a daily update adds
a small new file instead of rewriting a large one. This puts it back
together, filtered however you need it.
"""
import argparse
import csv
import sys
from pathlib import Path

DATA = Path(__file__).resolve().parent / 'data'
FIELDS = ['timestamp_utc', 'zone', 'price_eur_mwh', 'resolution_min']


def rows(zone=None, resolution=None, start=None, end=None):
    for f in sorted(DATA.rglob('*.csv')):
        if f.stem == 'latest':
            continue
        if start and f.stem < start:
            continue
        if end and f.stem > end:
            continue
        with f.open(encoding='utf-8') as fh:
            for r in csv.DictReader(fh):
                if zone and r['zone'] != zone:
                    continue
                if resolution and r['resolution_min'] != str(resolution):
                    continue
                yield r


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--zone', help='e.g. CZ, DE-LU, IT-North')
    p.add_argument('--resolution', type=int, choices=[15, 30, 60],
                   help='minutes per point; DE-LU and AT publish both 60 and 15')
    p.add_argument('--from', dest='start', metavar='YYYY-MM-DD')
    p.add_argument('--to', dest='end', metavar='YYYY-MM-DD')
    a = p.parse_args()

    w = csv.DictWriter(sys.stdout, FIELDS)
    w.writeheader()
    n = 0
    for r in rows(a.zone, a.resolution, a.start, a.end):
        w.writerow(r)
        n += 1
    if not n:
        print('no rows matched — check the zone code and the date range',
              file=sys.stderr)
        return 1
    print(f'{n} rows', file=sys.stderr)
    return 0


if __name__ == '__main__':
    sys.exit(main())
