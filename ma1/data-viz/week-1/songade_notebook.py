import marimo

__generated_with = "0.24.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as ma
    import polars as pl
    import folium
    from geopy.geocoders import Nominatim
    from folium.plugins import MarkerCluster

    return MarkerCluster, Nominatim, folium, pl


@app.cell
def _(pl):
    sondage_path = "./week-1/SondageVI26.xlsx"

    sondage_data = pl.read_excel(sondage_path)
    sondage_data.head()
    return (sondage_data,)


@app.cell
def _(sondage_data):
    sondage_data.describe()
    return


@app.cell
def _(sondage_data):
    cities = sondage_data.get_column(
        "Dans quelle ville habitez-vous ?"
    ).value_counts()
    cities
    return


@app.cell
def _(pl, sondage_data):
    sondage_data_clean = sondage_data.with_columns(
        pl.col("Dans quelle ville habitez-vous ?").replace(
            {"Corgémont (Jura Bernois) mais pour le Master Renens": "Renens"}
        )
    )
    return (sondage_data_clean,)


@app.cell
def _(sondage_data_clean):
    cities_clean = sondage_data_clean.get_column(
        "Dans quelle ville habitez-vous ?"
    ).value_counts()
    return (cities_clean,)


@app.cell
def _(geolocator):
    def geocode(city):
        loc = geolocator.geocode(f"{city}, Switzerland", timeout=10)
        return (loc.latitude, loc.longitude) if loc else None

    return (geocode,)


@app.cell
def _(Nominatim):
    geolocator = Nominatim(user_agent="sondage-dataviz")
    return (geolocator,)


@app.cell
def _(cities_clean, geocode, pl):
    geocoded_cities = cities_clean.with_columns(
        pl.col("Dans quelle ville habitez-vous ?")
        .map_elements(geocode, return_dtype=pl.Object)
        .alias("coords")
    )
    return (geocoded_cities,)


@app.cell
def _(geocoded_cities):
    geocoded_cities
    return


@app.cell
def _(MarkerCluster, folium):
    m = folium.Map(location=[46.8, 8.2], zoom_start=8, tiles="Esri WorldImagery")
    cluster = MarkerCluster().add_to(m)
    return cluster, m


@app.cell
def _(folium, m):
    folium.TileLayer(
        tiles="https://{s}.basemaps.cartocdn.com/light_only_labels/{z}/{x}/{y}{r}.png",
        attr="CartoDB",
        name="labels",
        overlay=True,
    ).add_to(m)
    return


@app.cell
def _(cluster, folium, geocoded_cities, m):
    for row in geocoded_cities.iter_rows(named=True):
        city = row["Dans quelle ville habitez-vous ?"]
        count = row["count"]
        lat, lon = row["coords"]
        size = 20  # grows with the count

        folium.Marker(
            location=[lat, lon],
            icon=folium.DivIcon(
                html=f"""
                    <div style="
                        background-color: #3186cc;
                        color: white;
                        width: {size}px;
                        height: {size}px;
                        border-radius: 50%;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        font-size: 12px;
                        font-weight: bold;
                        border: 2px solid white;
                        box-shadow: 0 0 4px rgba(0,0,0,0.4);
                    ">{count}</div>
                """,
                icon_size=(size, size),
                icon_anchor=(size // 2, size // 2),
            ),
            tooltip=f"{city} — {count} personne(s)",
        ).add_to(cluster)

    m.save("./week-1/map.html")
    m
    return


if __name__ == "__main__":
    app.run()
