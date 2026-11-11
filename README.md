# House prices in Ireland, 2011 to 2024

My Leaving Certificate Computer Science project: a Flask site that analyses how Irish house prices changed each year, region by region, using the Central Statistics Office's Residential Property Price Index.

**Live:** https://irish-house-prices.vercel.app

## What it does

- **14 regions:** national, Dublin and its four council areas, and the rest of the country by region.
- **For each region:** the mean, median and mode of the yearly change; the biggest rise and fall; and the total change since January 2010, worked out by chaining the yearly figures.
- **A line graph** comparing up to four regions, drawn on the server with matplotlib.
- **A year-by-year table.**
- **Dark mode and bigger text switches,** kept from the original project for accessibility.

Some things the data shows: prices fell about 20% nationally in the year to January 2012, rose every year from 2014, and by January 2024 were about 57% above January 2010.

## How it's built

| Part | What it does |
|---|---|
| `app.py` | Flask app. pandas loads and cleans the CSV, works out the statistics and serves them as JSON at `/api/summary`. `/graph.png` draws the graph with matplotlib. |
| `templates/index.html` | The page. Plain JavaScript asks the API for a region's numbers and swaps the graph. |
| `data/rppi-12-month-change.csv` | CSO figures: 12-month % change in house prices, each January, 2011 to 2024. |
| `tests/test_app.py` | pytest: data checks, the statistics against hand-worked values, the API and the graph. |

## Tidied up in 2026

Before putting it online I:

- **Fixed the graph,** which read a "Monthly Income" column the data doesn't have, so it never drew.
- **Graphed what the data actually is:** one figure per region each January. It had been treated as monthly data for one area.
- **Made the mode honest:** it showed the smallest value when nothing repeats, and now says there's no mode.
- **Added more figures:** per-region statistics, the overall change and the biggest rise and fall.
- **Removed the login and sign-up pages:** they saved passwords unprotected in a test database, and you don't need an account to view the analysis. Also removed links to pages that weren't in the project.
- **Added a new layout, tests and this README.**

## Run it

```
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
flask --app app run      # http://localhost:5000
pytest
```

Data: Central Statistics Office, Ireland.

---

Built by [Cian McCaul](https://cianmccaul.vercel.app).
