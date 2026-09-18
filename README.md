# European day-ahead electricity prices

Day-ahead auction prices for **39 European bidding zones**, back to January
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
| **Zones** | AT · BE · CH · CZ · DE-LU · DK1 · DK2 · EE · ES · FI · FR · GB · GR · HR · HU · IT-North · IT-CNorth · IT-CSouth · IT-South · IT-Sicily · IT-Sardinia · LT · LV · NL · NO1 · NO2 · NO3 · NO4 · NO5 · PL · PT · RO · RS · SE1 · SE2 · SE3 · SE4 · SI · SK |
| **From** | 2021-12-31 |
| **Updated** | daily, a few hours after each auction clears |
| **Unit** | EUR/MWh, the day-ahead auction result |
| **Source** | [ENTSO-E Transparency Platform](https://transparency.entsoe.eu) |
| **Size** | about 96 MB |

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

**Day-ahead only, one series per zone.** ENTSO-E returns several price series
in one response: the day-ahead auction, intraday auctions, and — where the
market runs both — an hourly and a quarter-hourly product for the same clock
time. Until 19 September 2026 this dataset mixed them, so a German day carried
two prices for the same hour and a naive mean belonged to neither product.

Now only the day-ahead auction is kept, identified by
`contract_MarketAgreement.type` A01 and the first classification sequence. That
is the series every reference publishes as *the* spot price — for Germany on
10 May 2022 it is the hourly 183.32 EUR/MWh, not the quarter-hourly 183.71 of
the separate auction.

`resolution_min` still matters, because the resolution of the day-ahead itself
changed: most zones moved from hourly to 15-minute products during 2025, so a
long series changes resolution partway through. It no longer distinguishes two
products within one zone and day.

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

**Gaps.** Until 19 September 2026 this dataset had holes in it — about 10 %
of rows — and this file used to blame the source for them. That was wrong.
ENTSO-E compresses runs of equal prices (`curveType` A03): it sends the first
interval of a run and omits the rest, and the collector here read it
position-by-position, so those intervals disappeared. The history has been
re-fetched and the collector fixed. If you pulled data before that date, pull
it again.

A genuine gap is still possible — a zone occasionally publishes 23 points for
a day with no DST involved. Check, don't assume.

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
  today's numbers for 38 zones, with a national page per market:
  [Spain](https://progrunners.com/es/precio-luz-hoy/) ·
  [Germany](https://progrunners.com/de/strompreis-boerse/) ·
  [Austria](https://progrunners.com/at/strompreis-oesterreich/) ·
  [Estonia](https://progrunners.com/et/elektri-hind/) ·
  [Finland](https://progrunners.com/fi/sahkon-hinta/) ·
  [Sweden](https://progrunners.com/sv/elpriser-idag/) ·
  [Norway](https://progrunners.com/no/strompriser-i-dag/) ·
  [Denmark](https://progrunners.com/da/elpriser-i-dag/) ·
  [Lithuania](https://progrunners.com/lt/elektros-kaina/) ·
  [Latvia](https://progrunners.com/lv/elektribas-cena/) ·
  [Netherlands](https://progrunners.com/nl/stroomprijs/) ·
  [Poland](https://progrunners.com/pl/ceny-pradu/) ·
  [France](https://progrunners.com/fr/prix-electricite/) ·
  [Italy](https://progrunners.com/it/prezzi-zonali/) ·
  [Slovenia](https://progrunners.com/sl/cena-elektrike/) ·
  [Czechia](https://progrunners.com/cs/spotova-cena-elektriny/)

Maintained by [progrunners](https://progrunners.com/open-source/) — we build
trading dashboards and market data pipelines for European power markets, and
publish the parts that are useful on their own.

**All of it in one place:** [progrunners.com/open-source](https://progrunners.com/open-source/)
— six repositories, what each one is for, and the one mistake worth reading
about before you trust any price series, ours included.
