import marimo

__generated_with = "0.24.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import polars as pl
    import matplotlib.pyplot as plt

    return pl, plt


@app.cell
def _(pl):
    raw_data = pl.read_excel("./week-2/Erwerbst_tigeCH.xls", engine="calamine")

    raw_data.columns = ["label", "1970", "1980", "1990", "2000"]

    YEARS = ["1970", "1980", "1990", "2000"]
    GROUPS = ["Männer", "Frauen", "Schweizer", "Ausländer",
              "Schweizerinnen", "Ausländerinnen"]

    df = (
        raw_data
        .filter(
            ~pl.col("label").str.contains("Tabelle 2|Quelle")
            & pl.col("label").is_not_null()
        )
        .with_columns(pl.col("label").str.strip_chars())
        .with_columns(pl.all().exclude("label").cast(pl.Int64, strict=False))
        .with_columns(
            pl.when(pl.col("label").is_in(GROUPS))
              .then(pl.col("label"))
              .otherwise(None)
              .fill_null(strategy="forward")
              .alias("group")
        )
        .filter(~pl.col("label").is_in(GROUPS))
        .with_columns(pl.col("group").fill_null("Gesamt"))
    )

    df.head()
    return YEARS, df


@app.cell
def _(df):
    df.describe()
    return


@app.cell
def _(df, pl):
    tot = df.filter(pl.col("label") == "Total").drop("label")
    pt = df.filter(pl.col("label") == "Teilzeit Erwerbstätige").drop("label")
    vt = df.filter(pl.col("label") == "Vollzeit Erwerbstätige").drop("label")

    print(f"Total: {tot}")
    print(f"Full time: {vt}")
    print(f"Part time: {pt}")
    return pt, tot, vt


@app.cell
def _(pt, tot, vt):
    tot_d = {r[-1]: r[:-1] for r in tot.iter_rows()}
    pt_d  = {r[-1]: r[:-1] for r in pt.iter_rows()}
    vt_d  = {r[-1]: r[:-1] for r in vt.iter_rows()}

    g, f, m = tot_d["Gesamt"], tot_d["Frauen"], tot_d["Männer"]
    return f, g, m, pt_d, tot_d, vt_d


@app.cell
def _(f, g, m, pl, pt_d, tot_d, vt_d):
    df_summary = pl.DataFrame({
        "indicateur": [
            "Part femmes 1970 (%)", "Part femmes 2000 (%)",
            "Croissance femmes 1970-2000 (%)", "Croissance hommes 1970-2000 (%)",
            "Femmes % emplois nets",
            "Temps partiel 1970 (%)", "Temps partiel 2000 (%)",
            "Temps partiel femmes 2000 (%)", "Temps partiel Suissesses 2000 (%)",
            "Temps plein 1990->2000", "Temps partiel % emplois nets",
        ],
        "valeur": [
            f[0]/g[0]*100, f[3]/g[3]*100,
            (f[3]/f[0]-1)*100, (m[3]/m[0]-1)*100,
            (f[3]-f[0])/(g[3]-g[0])*100,
            pt_d["Gesamt"][0]/g[0]*100, pt_d["Gesamt"][3]/g[3]*100,
            pt_d["Frauen"][3]/tot_d["Frauen"][3]*100,
            pt_d["Schweizerinnen"][3]/tot_d["Schweizerinnen"][3]*100,
            vt_d["Gesamt"][3]-vt_d["Gesamt"][2],
            (pt_d["Gesamt"][3]-pt_d["Gesamt"][0])/(g[3]-g[0])*100,
        ],
    })

    df_summary
    return


@app.cell
def _(YEARS, pl, pt, tot):
    pt_rate = pt.with_columns([pl.col(y) / pl.first(y) for y in YEARS]).join(
        tot.select(["group"] + YEARS), on="group", suffix="_tot"
    )

    gmap = {
        "Männer": "Hommes",
        "Frauen": "Femmes",
        "Schweizer": "Suisses",
        "Ausländer": "Étrangers",
        "Schweizerinnen": "Suissesses",
        "Ausländerinnen": "Étrangères",
        "Gesamt": "Ensemble",
    }

    fr = tot.filter(pl.col("group") == "Frauen").select(YEARS).row(0)
    ge = tot.filter(pl.col("group") == "Gesamt").select(YEARS).row(0)
    share_f = [f / g * 100 for f, g in zip(fr, ge)]
    return gmap, pt_rate, share_f


@app.cell
def _(YEARS, plt, share_f):
    _fig, _ax = plt.subplots(figsize=(8, 4.8))
    _ax.plot(YEARS, share_f, marker="o", lw=3, color="#c2185b")
    for x, y in zip(YEARS, share_f):
        _ax.annotate(
            f"{y:.1f}%",
            (x, y),
            textcoords="offset points",
            xytext=(0, 10),
            ha="center",
        )
    _ax.set_title(
        "Part des femmes dans l'emploi total en Suisse, 1970–2000",
        weight="bold",
    )
    _ax.set_ylabel("% de l'emploi total")
    _ax.set_ylim(25, 50)
    _ax.spines[["top", "right"]].set_visible(False)
    _fig.tight_layout()
    _fig.savefig("./week-2/viz1_feminisation.png", dpi=150)
    plt.show()
    return


@app.cell
def _():
    order = [
        "Frauen",
        "Schweizerinnen",
        "Ausländerinnen",
        "Gesamt",
        "Schweizer",
        "Männer",
        "Ausländer",
    ]
    colors = {
        "Gesamt": "#333333",
        "Frauen": "#c2185b",
        "Schweizerinnen": "#e91e63",
        "Ausländerinnen": "#f48fb1",
        "Männer": "#1565c0",
        "Schweizer": "#42a5f5",
        "Ausländer": "#90caf9",
    }
    return colors, order


@app.cell
def _(YEARS, colors, gmap, order, pl, plt, pt_rate):
    _fig, _ax = plt.subplots(figsize=(8, 4.8))
    for _gname in order:
        r = pt_rate.filter(pl.col("group") == _gname).select(YEARS).row(0)
        r = [v * 100 for v in r]
        _ax.plot(
            YEARS,
            r,
            marker="o",
            lw=2.5 if _gname == "Gesamt" else 1.8,
            color=colors[_gname],
            label=gmap[_gname],
        )
        _ax.annotate(
            f"{r[-1]:.0f}%",
            (3, r[-1]),
            textcoords="offset points",
            xytext=(6, 0),
            fontsize=9,
            color=colors[_gname],
        )
    _ax.set_title(
        "Taux d'emploi à temps partiel par groupe, 1970–2000", weight="bold"
    )
    _ax.set_ylabel("% du groupe")
    _ax.set_xlim(-0.3, 3.8)
    _ax.legend(frameon=False, fontsize=9, loc="upper left")
    _ax.spines[["top", "right"]].set_visible(False)
    _fig.tight_layout()
    _fig.savefig("./week-2/viz2_tempspartiel.png", dpi=150)
    plt.show()
    return


@app.cell
def _():
    gorder = [
        "Gesamt",
        "Männer",
        "Frauen",
        "Schweizer",
        "Ausländer",
        "Schweizerinnen",
        "Ausländerinnen",
    ]
    return (gorder,)


@app.cell
def _(YEARS, gmap, gorder, pl, plt, pt, vt):
    _fig, _axes = plt.subplots(2, 4, figsize=(13, 6.5), sharex=True)
    _axes = _axes.ravel()
    for i, _gname in enumerate(gorder):
        ax = _axes[i]
        v = [
            x / 1000
            for x in vt.filter(pl.col("group") == _gname).select(YEARS).row(0)
        ]
        t = [
            x / 1000
            for x in pt.filter(pl.col("group") == _gname).select(YEARS).row(0)
        ]
        ax.bar(YEARS, v, color="#1565c0", label="Temps plein")
        ax.bar(YEARS, t, bottom=v, color="#e91e63", label="Temps partiel")
        ax.set_title(gmap[_gname], weight="bold")
        ax.set_ylim(0, 3100)
        ax.spines[["top", "right"]].set_visible(False)
        if i % 4 == 0:
            ax.set_ylabel("milliers")
    _axes[7].axis("off")
    _axes[7].legend(
        *_axes[0].get_legend_handles_labels(),
        loc="center",
        frameon=False,
        fontsize=12,
    )
    _fig.suptitle(
        "Employés actifs selon le degré d'occupation, par groupe — "
        "intégralité du tableau (OFS, 1970–2000)",
        weight="bold",
    )
    _fig.tight_layout(rect=[0, 0, 1, 0.95])
    _fig.savefig("./week-2/viz3_integralite.png", dpi=150)
    plt.show()
    return


if __name__ == "__main__":
    app.run()
