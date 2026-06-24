import streamlit as st
import pandas as pd

from modules.helpers import *


def finn_sesongstype(season):
    season = str(season).upper().strip()

    if "NOOS" in season:
        return "NOOS"
    if season.startswith("AW"):
        return "AW"
    if season.startswith("SS"):
        return "SS"

    return "UKJENT"


def klargjor_lager(df):
    df = df.copy()
    df["Lagerkostnad"] = df["Cost"].apply(tekst_til_tall)
    df["Antall_lager"] = df["Qty"].apply(tekst_til_tall)
    df["Produktnøkkel"] = df["Name"].apply(normaliser_tekst)

    if "Season" in df.columns:
        df["Sesongstype"] = df["Season"].apply(finn_sesongstype)
    else:
        df["Sesongstype"] = "UKJENT"

    return df


def klargjor_salg(df):
    df = df.copy()
    df["Antall_solgt"] = df["Qty"].apply(tekst_til_tall)
    df["Omsetning"] = df["Price"].apply(tekst_til_tall)
    df["Rabatt"] = df["Discount"].apply(tekst_til_tall)
    df["Varekost_solgt"] = df["Cost"].apply(tekst_til_tall)
    df["Produktnavn"] = df["PRODUCTID_FK"].apply(hent_produktnavn_fra_salg)
    df["Produktnøkkel"] = df["Produktnavn"].apply(normaliser_tekst)
    df = df[df["Produktnøkkel"] != ""]
    df["Bruttofortjeneste"] = df["Omsetning"] - df["Varekost_solgt"]
    return df


def analyser_lagerverdi(df):
    df = klargjor_lager(df)

    if "TotalKost" in df.columns:
        total_kostnad = tekst_til_tall(df["TotalKost"].iloc[0])
    else:
        total_kostnad = df["Lagerkostnad"].sum()

    if "textbox62" in df.columns:
        antall_enheter = tekst_til_tall(df["textbox62"].iloc[0])
    else:
        antall_enheter = df["Antall_lager"].sum()

    antall_produkter = df["Name"].nunique()

    col1, col2, col3 = st.columns(3)
    col1.metric("Lagerkostnad", kr(total_kostnad))
    col2.metric("Antall på lager", f"{antall_enheter:,.0f}".replace(",", " "))
    col3.metric("Unike produkter", antall_produkter)

    produkt = (
        df.groupby("Name")[["Antall_lager", "Lagerkostnad"]]
        .sum()
        .sort_values("Lagerkostnad", ascending=False)
    )

    merke = (
        df.groupby("Brand")[["Antall_lager", "Lagerkostnad"]]
        .sum()
        .sort_values("Lagerkostnad", ascending=False)
    )

    gruppe = (
        df.groupby("Group")[["Antall_lager", "Lagerkostnad"]]
        .sum()
        .sort_values("Lagerkostnad", ascending=False)
    )

    sesong = (
        df.groupby("Sesongstype")[["Antall_lager", "Lagerkostnad"]]
        .sum()
        .sort_values("Lagerkostnad", ascending=False)
    )

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
        ["Oversikt", "Produkter", "Merker", "Varegrupper", "Sesong", "Analyse"]
    )

    with tab1:
        c1, c2 = st.columns(2)

        with c1:
            st.subheader("Produkter som binder mest kapital")
            st.dataframe(formater_tabell(produkt.head(20)), use_container_width=True)

        with c2:
            st.subheader("Lagerkostnad per merke")
            st.bar_chart(merke["Lagerkostnad"].head(10))

    with tab2:
        st.subheader("Alle produkter")
        st.dataframe(formater_tabell(produkt), use_container_width=True)

    with tab3:
        st.subheader("Lagerkostnad per merke")
        st.dataframe(formater_tabell(merke), use_container_width=True)
        st.bar_chart(merke["Lagerkostnad"].head(15))

    with tab4:
        st.subheader("Lagerkostnad per varegruppe")
        st.dataframe(formater_tabell(gruppe), use_container_width=True)
        st.bar_chart(gruppe["Lagerkostnad"].head(15))

    with tab5:
        st.subheader("Lagerkostnad per sesongstype")
        st.dataframe(formater_tabell(sesong), use_container_width=True)
        st.bar_chart(sesong["Lagerkostnad"])

    with tab6:
        st.subheader("Analyse og innsikt")
        st.success(f"Total lagerkostnad er {kr(total_kostnad)}.")
        st.write(f"Produktet som binder mest kapital er **{produkt.index[0]}**.")
        st.write(f"Merket som binder mest kapital er **{merke.index[0]}**.")
        st.write(f"Varegruppen som binder mest kapital er **{gruppe.index[0]}**.")
        st.warning(
            "Last også opp salgsrapport for å finne slow movers, fast movers og reorder-kandidater."
        )


def analyser_front_salg(df):
    df = klargjor_salg(df)

    total_omsetning = df["Omsetning"].sum()
    total_antall = df["Antall_solgt"].sum()
    total_rabatt = df["Rabatt"].sum()
    total_fortjeneste = df["Bruttofortjeneste"].sum()
    margin = (total_fortjeneste / total_omsetning * 100) if total_omsetning else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Omsetning", kr(total_omsetning))
    col2.metric("Antall solgt", f"{total_antall:,.0f}".replace(",", " "))
    col3.metric("Rabatt", kr(total_rabatt))
    col4.metric("Bruttomargin", f"{margin:.1f}%")

    produkt = (
        df.groupby("Produktnavn")[[
            "Antall_solgt",
            "Omsetning",
            "Rabatt",
            "Varekost_solgt",
            "Bruttofortjeneste"
        ]]
        .sum()
        .sort_values("Omsetning", ascending=False)
    )

    produkt["Margin %"] = (
        produkt["Bruttofortjeneste"] / produkt["Omsetning"] * 100
    ).round(1)

    merke = (
        df.groupby("Brand")[[
            "Antall_solgt",
            "Omsetning",
            "Rabatt",
            "Varekost_solgt",
            "Bruttofortjeneste"
        ]]
        .sum()
        .sort_values("Omsetning", ascending=False)
    )

    merke["Margin %"] = (
        merke["Bruttofortjeneste"] / merke["Omsetning"] * 100
    ).round(1)

    gruppe = (
        df.groupby("Group")[[
            "Antall_solgt",
            "Omsetning",
            "Rabatt",
            "Varekost_solgt",
            "Bruttofortjeneste"
        ]]
        .sum()
        .sort_values("Omsetning", ascending=False)
    )

    gruppe["Margin %"] = (
        gruppe["Bruttofortjeneste"] / gruppe["Omsetning"] * 100
    ).round(1)

    tab1, tab2, tab3, tab4 = st.tabs(
        ["Produkter", "Merker", "Varegrupper", "Analyse"]
    )

    with tab1:
        st.subheader("Bestselgende produkter")
        st.dataframe(formater_tabell(produkt.head(30)), use_container_width=True)
        st.bar_chart(produkt["Omsetning"].head(15))

    with tab2:
        st.subheader("Salg per merke")
        st.dataframe(formater_tabell(merke), use_container_width=True)
        st.bar_chart(merke["Omsetning"].head(15))

    with tab3:
        st.subheader("Salg per varegruppe")
        st.dataframe(formater_tabell(gruppe), use_container_width=True)
        st.bar_chart(gruppe["Omsetning"].head(15))

    with tab4:
        st.success(f"Total omsetning er {kr(total_omsetning)}.")
        st.write(f"Bestselgende produkt er **{produkt.index[0]}**.")
        st.write(f"Sterkeste merke er **{merke.index[0]}**.")
        st.write(f"Sterkeste varegruppe er **{gruppe.index[0]}**.")


def analyser_lager_og_salg(lager_df, salg_df):
    lager = klargjor_lager(lager_df)
    salg = klargjor_salg(salg_df)

    lager_produkt = lager.groupby("Produktnøkkel").agg(
        Produkt=("Name", "first"),
        Merke_lager=("Brand", "first"),
        Varegruppe_lager=("Group", "first"),
        Sesongstype=("Sesongstype", "first"),
        Antall_lager=("Antall_lager", "sum"),
        Lagerkostnad=("Lagerkostnad", "sum"),
    ).reset_index()

    salg_produkt = salg.groupby("Produktnøkkel").agg(
        Produkt_salg=("Produktnavn", "first"),
        Merke_salg=("Brand", "first"),
        Varegruppe_salg=("Group", "first"),
        Antall_solgt=("Antall_solgt", "sum"),
        Omsetning=("Omsetning", "sum"),
        Rabatt=("Rabatt", "sum"),
        Varekost_solgt=("Varekost_solgt", "sum"),
        Bruttofortjeneste=("Bruttofortjeneste", "sum"),
    ).reset_index()

    analyse = lager_produkt.merge(
        salg_produkt,
        on="Produktnøkkel",
        how="outer"
    )

    analyse["Produkt"] = analyse["Produkt"].fillna(analyse["Produkt_salg"])
    analyse["Sesongstype"] = analyse["Sesongstype"].fillna("UKJENT")

    for c in [
        "Antall_lager",
        "Lagerkostnad",
        "Antall_solgt",
        "Omsetning",
        "Rabatt",
        "Bruttofortjeneste"
    ]:
        analyse[c] = analyse[c].fillna(0)

    analyse["Sell-through %"] = (
        analyse["Antall_solgt"]
        / (analyse["Antall_solgt"] + analyse["Antall_lager"])
        * 100
    ).replace([float("inf")], 0).fillna(0).round(1)

    analyse["Margin %"] = (
        analyse["Bruttofortjeneste"] / analyse["Omsetning"] * 100
    ).replace([float("inf")], 0).fillna(0).round(1)

    valgt_sesong = st.selectbox(
        "Analyser sesong",
        ["NOOS", "SS", "AW", "Alle"],
        help="NOOS vurderes alltid. SS/AW vurderes når du ønsker å analysere aktuell sesong."
    )

    if valgt_sesong == "Alle":
        sesonger_som_skal_vurderes = ["NOOS", "SS", "AW"]
    else:
        sesonger_som_skal_vurderes = ["NOOS", valgt_sesong]

    analyse["Status"] = "Normal"

    analyse.loc[
        (analyse["Sesongstype"].isin(sesonger_som_skal_vurderes))
        & (analyse["Lagerkostnad"] > 0)
        & (analyse["Antall_solgt"] == 0),
        "Status"
    ] = "Kritisk slow mover"

    analyse.loc[
        (analyse["Sesongstype"].isin(sesonger_som_skal_vurderes))
        & (analyse["Lagerkostnad"] > 0)
        & (analyse["Sell-through %"] < 20)
        & (analyse["Antall_solgt"] > 0),
        "Status"
    ] = "Slow mover"

    analyse.loc[
        (~analyse["Sesongstype"].isin(sesonger_som_skal_vurderes))
        & (analyse["Sesongstype"].isin(["SS", "AW"])),
        "Status"
    ] = "Utenfor valgt sesong"

    analyse.loc[
        (analyse["Sesongstype"].isin(sesonger_som_skal_vurderes))
        & (analyse["Antall_lager"] <= 3)
        & (analyse["Antall_solgt"] >= 5),
        "Status"
    ] = "Reorder-kandidat"

    analyse.loc[
        (analyse["Sesongstype"].isin(sesonger_som_skal_vurderes))
        & (analyse["Sell-through %"] >= 70)
        & (analyse["Antall_lager"] > 0),
        "Status"
    ] = "Sterk vare"

    if valgt_sesong != "Alle":
        analyse = analyse[
            (analyse["Sesongstype"] == valgt_sesong)
            | (analyse["Sesongstype"] == "NOOS")
        ]

    total_lager = analyse["Lagerkostnad"].sum()
    total_salg = analyse["Omsetning"].sum()
    total_fortjeneste = analyse["Bruttofortjeneste"].sum()

    slow_count = len(
        analyse[
            analyse["Status"].isin(["Slow mover", "Kritisk slow mover"])
        ]
    )

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Lagerkostnad", kr(total_lager))
    col2.metric("Omsetning", kr(total_salg))
    col3.metric("Bruttofortjeneste", kr(total_fortjeneste))
    col4.metric("Slow movers", slow_count)
    col5.metric("Sesong", valgt_sesong)

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
        ["Oversikt", "Slow movers", "Reorder", "Sterke varer", "Sesong", "Analyse"]
    )

    with tab1:
        vis = analyse.sort_values("Lagerkostnad", ascending=False)

        st.dataframe(
            formater_tabell(
                vis[
                    [
                        "Produkt",
                        "Sesongstype",
                        "Antall_lager",
                        "Antall_solgt",
                        "Lagerkostnad",
                        "Omsetning",
                        "Bruttofortjeneste",
                        "Sell-through %",
                        "Margin %",
                        "Status"
                    ]
                ].head(50)
            ),
            use_container_width=True,
        )

    with tab2:
        slow = analyse[
            analyse["Status"].isin(["Slow mover", "Kritisk slow mover"])
        ].sort_values("Lagerkostnad", ascending=False)

        st.dataframe(
            formater_tabell(
                slow[
                    [
                        "Produkt",
                        "Sesongstype",
                        "Antall_lager",
                        "Antall_solgt",
                        "Lagerkostnad",
                        "Omsetning",
                        "Sell-through %",
                        "Status"
                    ]
                ]
            ),
            use_container_width=True,
        )

    with tab3:
        reorder = analyse[
            analyse["Status"] == "Reorder-kandidat"
        ].sort_values("Antall_solgt", ascending=False)

        st.dataframe(
            formater_tabell(
                reorder[
                    [
                        "Produkt",
                        "Sesongstype",
                        "Antall_lager",
                        "Antall_solgt",
                        "Omsetning",
                        "Bruttofortjeneste",
                        "Sell-through %",
                        "Status"
                    ]
                ]
            ),
            use_container_width=True,
        )

    with tab4:
        sterke = analyse[
            analyse["Status"] == "Sterk vare"
        ].sort_values("Omsetning", ascending=False)

        st.dataframe(
            formater_tabell(
                sterke[
                    [
                        "Produkt",
                        "Sesongstype",
                        "Antall_lager",
                        "Antall_solgt",
                        "Omsetning",
                        "Bruttofortjeneste",
                        "Sell-through %",
                        "Status"
                    ]
                ]
            ),
            use_container_width=True,
        )

    with tab5:
        sesong = (
            analyse.groupby("Sesongstype")[[
                "Antall_lager",
                "Antall_solgt",
                "Lagerkostnad",
                "Omsetning",
                "Bruttofortjeneste"
            ]]
            .sum()
            .sort_values("Lagerkostnad", ascending=False)
        )

        st.subheader("Analyse per sesongstype")
        st.dataframe(formater_tabell(sesong), use_container_width=True)
        st.bar_chart(sesong["Lagerkostnad"])

    with tab6:
        st.success(f"Lageret binder {kr(total_lager)} i kost.")
        st.info(f"Salgsrapporten viser {kr(total_salg)} i omsetning.")
        st.write(f"Det er **{slow_count}** produkter som bør vurderes som slow movers.")

        st.info(
            "NOOS vurderes alltid. Når du velger SS eller AW, vises den valgte sesongen sammen med NOOS."
        )

        if slow_count > 0:
            topp_slow = (
                analyse[
                    analyse["Status"].isin(["Slow mover", "Kritisk slow mover"])
                ]
                .sort_values("Lagerkostnad", ascending=False)
                .iloc[0]
            )

            st.warning(
                f"Viktigste slow mover er **{topp_slow['Produkt']}**, "
                f"som binder {kr(topp_slow['Lagerkostnad'])}."
            )