import pytest

from app import REGIONS, app, df, summary


@pytest.fixture
def client():
    app.config["TESTING"] = True
    return app.test_client()


def test_data_has_every_region_for_every_year():
    assert len(REGIONS) == 14
    assert df.groupby("region")["year"].count().eq(14).all()
    assert (df["year"].min(), df["year"].max()) == (2011, 2024)


def test_national_figures():
    s = summary("National")
    assert s["mean"] == 3.8
    assert s["median"] == 5.9  # halfway between 5.4 and 6.4
    assert s["best"] == {"year": 2015, "change": 17.5}
    assert s["worst"] == {"year": 2012, "change": -20.0}


def test_mode_is_none_when_nothing_repeats():
    assert summary("National")["mode"] == []


def test_mode_when_a_value_repeats():
    # Dublin City was +3.4% in both 2015 and 2016
    assert 3.4 in summary("Dublin City")["mode"]


def test_overall_change_chains_the_years():
    s = summary("National")
    expected = 1.0
    for y in s["years"]:
        expected *= 1 + y["change"] / 100
    assert s["overall"] == round((expected - 1) * 100, 1)


def test_page_and_api(client):
    assert client.get("/").status_code == 200
    assert client.get("/api/summary?region=West").get_json()["region"] == "West"
    assert client.get("/api/summary?region=Atlantis").status_code == 404


def test_graph_is_a_png_and_ignores_unknown_regions(client):
    res = client.get("/graph.png?region=Dublin&region=West&region=Atlantis")
    assert res.status_code == 200
    assert res.mimetype == "image/png"
    assert res.data[:8] == b"\x89PNG\r\n\x1a\n"
