"""
House prices in Ireland, 2011 to 2024.

My Leaving Certificate Computer Science project: a small Flask site that
analyses the Central Statistics Office's Residential Property Price Index.
For each region it gives the yearly change in house prices (January to
January), the mean, median and mode of those changes, how far prices moved
overall since January 2010, and a line graph drawn with matplotlib.
"""

import io
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # draw graphs without a screen (on a server)
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
from flask import Flask, Response, abort, jsonify, render_template, request  # noqa: E402

app = Flask(__name__)

DATA = Path(__file__).parent / "data" / "rppi-12-month-change.csv"


def load(path=DATA):
    """Read the CSO data into one row per region per year."""
    df = pd.read_csv(path)
    df = df.rename(columns={"Type of Residential Property": "region", "percentageChange": "change"})
    df["year"] = df["Month"].str[:4].astype(int)
    df["region"] = df["region"].str.replace(" - houses", "", regex=False)
    return df[["region", "year", "change"]].sort_values(["region", "year"]).reset_index(drop=True)


df = load()
REGIONS = ["National"] + sorted(r for r in df["region"].unique() if r != "National")
FIRST_YEAR, LAST_YEAR = int(df["year"].min()), int(df["year"].max())


def summary(region):
    """The numbers for one region: mean, median and mode of the yearly changes, and more."""
    rows = df[df["region"] == region]
    changes = rows["change"]
    modes = changes.mode()
    best = rows.loc[changes.idxmax()]
    worst = rows.loc[changes.idxmin()]
    # Each figure is the change since the January before, so chaining them all
    # gives the total change since January 2010.
    overall = ((1 + changes / 100).prod() - 1) * 100
    return {
        "region": region,
        "mean": round(float(changes.mean()), 1),
        "median": round(float(changes.median()), 1),
        # Every value appears once in most regions, so "no mode" is the honest answer there.
        "mode": [float(m) for m in modes] if len(modes) < len(changes) else [],
        "best": {"year": int(best["year"]), "change": float(best["change"])},
        "worst": {"year": int(worst["year"]), "change": float(worst["change"])},
        "overall": round(float(overall), 1),
        "since": FIRST_YEAR - 1,
        "years": [{"year": int(y), "change": float(c)} for y, c in zip(rows["year"], changes)],
    }


@app.get("/")
def index():
    return render_template("index.html", regions=REGIONS, first=FIRST_YEAR, last=LAST_YEAR, national=summary("National"))


@app.get("/api/summary")
def api_summary():
    region = request.args.get("region", "National")
    if region not in REGIONS:
        abort(404)
    return jsonify(summary(region))


@app.get("/graph.png")
def graph():
    """A line graph of the yearly change for up to four regions."""
    chosen = [r for r in request.args.getlist("region") if r in REGIONS][:4] or ["National"]
    fig, ax = plt.subplots(figsize=(9, 4.6), dpi=110)
    colours = ["#17777C", "#C2410C", "#6D28D9", "#B45309"]
    for colour, region in zip(colours, chosen):
        rows = df[df["region"] == region]
        ax.plot(rows["year"], rows["change"], marker="o", linewidth=2.2, color=colour, label=region)
    ax.axhline(0, color="#15343A", linewidth=1)
    ax.set_xticks(range(FIRST_YEAR, LAST_YEAR + 1))
    ax.tick_params(axis="x", rotation=45)
    ax.set_ylabel("Change on a year earlier (%)")
    ax.set_title("House prices: change over 12 months, each January", loc="left", fontsize=12)
    ax.grid(axis="y", color="#E1EAEA")
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.legend(frameon=False)
    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    plt.close(fig)
    return Response(buf.getvalue(), mimetype="image/png", headers={"Cache-Control": "public, max-age=86400"})


if __name__ == "__main__":
    app.run(debug=True, port=5001)
