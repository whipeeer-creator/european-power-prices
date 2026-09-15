# European day-ahead electricity prices

Day-ahead auction prices for **12 European bidding zones**, back to January
2022, as plain CSV. Updated every day, automatically.

No account, no API key, no XML. `git clone` or a single `curl`.

```bash
curl -s https://raw.githubusercontent.com/whipeeer-creator/european-power-prices/main/data/latest.csv | head -5
```

```csv
timestamp_utc,zone,price_eur_mwh,resolution_min
2026-09-15T00:00:00Z,AT,218.18,15
2026-09-15T00:00:00Z,BE,218.18,60
2026-09-15T00:00:00Z,CZ,207.50,15
2026-09-15T00:00:00Z,DE-LU,213.02,60
```

## Why this exists

The prices are public, but getting a usable history is tedious. OTE makes you
click through day by day. ENTSO-E has everything but wants a token that arrives
by e-mail days later, and answers in XML with a resolution that changes
mid-series. Most people end up writing the same scraper again.

This is that scraper's output, kept up to date so nobody has to write it a
third time.

## What is in here

| | |
|---|---|
| **Zones** | CZ · DE-LU · AT · SK · PL · HU · SI · FR · NL · BE · ES · IT-North |
| **From** | 1 January 2022 |
| **Updated** | daily, a few hours after each auction clears |
| **Unit** | EUR/MWh, the day-ahead auction result |
| **Source** | [ENTSO-E Transparency Platform](https://transparency.entsoe.eu) |
| **Size** | about 40 MB |

```
data/2026/2026-09-15.csv      one delivery day, all zones
data/latest.csv               the last 7 days, for a quick look
merge.py                      put the daily files back together
```

**Why one file per day** rather than one big CSV: git stores a complete new
copy of a file every time it changes. Appending to a single large file once a
day would grow the repository by hundreds of megabytes a year. This way each
day adds one small file and nothing is rewritten.

## Use it

```bash
# one zone, one period
python3 merge.py --zone CZ --from 2024-01-01 > cz.csv

# German hourly product only (see the note on resolution below)
python3 merge.py --zone DE-LU --resolution 60 --from 2025-01-01 > de.csv
```

```python
import csv, glob

rows = []
for f in sorted(glob.glob('data/2026/*.csv')):
    with open(f) as fh:
        rows += [r for r in csv.DictReader(fh)
                 if r['zone'] == 'CZ' and r['resolution_min'] == '60']

prices = [float(r['price_eur_mwh']) for r in rows]
print(f'{len(prices)} hours, mean {sum(prices)/len(prices):.1f} EUR/MWh')
```

```python
# pandas, if you have it
import pandas as pd, glob
df = pd.concat(pd.read_csv(f) for f in glob.glob('data/*/*.csv'))
df['timestamp_utc'] = pd.to_datetime(df.timestamp_utc)
```

## Read this before you use the numbers

**Two resolutions can coexist, and mixing them is a real mistake.** Germany
and Austria clear an hourly *and* a quarter-hourly day-ahead product — two
different auctions with two different prices for the same clock time. Both are
in here, distinguished by `resolution_min`. If you filter on zone alone you
will get 120 rows for one German day and a mean that belongs to neither
product. **Always filter on `resolution_min` as well.** Most other zones moved
from hourly to 15-minute products during 2025, so a long series changes
resolution partway through.

**Timestamps are UTC**, and mark the *start* of the interval. Bidding zones
live in local time, so a delivery day is not a calendar day in this file —
`2026-09-15.csv` holds what ENTSO-E published for that UTC day. Convert before
you group by "day", or your daily averages will be shifted by one or two hours
depending on the season.

**Negative prices are real, not errors.** Between 2 and 7 % of points per zone
are below zero. When wind and solar push hard into a low load, clearing below
zero is cheaper than curtailing. The floor is −500 EUR/MWh in most zones.

**This is the wholesale auction price only.** It is not what anyone pays on a
bill. Grid fees, levies, taxes and supplier margin sit on top, and they are
usually larger than this number.

**Gaps happen.** A missing hour is almost always missing at the source, not
lost here — occasionally a zone publishes 23 points for a day with no DST
involved. Check, don't assume.

## How it stays current

A collector on our server pulls the auction results from ENTSO-E and commits
here. It re-fetches the last few days on every run, so a value the platform
corrects after publication gets corrected here too.

If a day is missing, the run failed rather than the price not existing. Open an
issue.

## Licence

The data is the published outcome of public auctions, redistributed under the
[ENTSO-E Transparency Platform terms](https://transparency.entsoe.eu). The code
in this repository is [MIT](LICENSE). Attribution to ENTSO-E as the original
source is appreciated by them and by us.

This is not a contractual reference. Do not settle trades against it.

## Related

- [entsoe-quickstart](https://github.com/whipeeer-creator/entsoe-quickstart) —
  single-file Python client, if you want to pull this yourself
- [eic-codes](https://github.com/whipeeer-creator/eic-codes) — the bidding zone
  codes used here, plus the traps that come with them
- [A practical guide to the ENTSO-E API](https://progrunners.com/entso-e-api/) —
  document types, resolutions, publication delays
- [Live European prices](https://progrunners.com/european-electricity-prices/) —
  today's numbers in a table, 38 zones

Maintained by [progrunners](https://progrunners.com/) — trading dashboards and
market data pipelines for European power markets.
