import streamlit as st
import pandas as pd

from modules.helpers import *
from modules.ai_konsulent import *


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

    if "Lagerkostnad" not in df.columns:
        if "Cost" in df.columns:
            df["Lagerkostnad"] = df["Cost"].apply(tekst_til_tall)
        elif "Kost" in df.columns:
            df["Lagerkostnad"] = df["Kost"].apply(tekst_til_tall)
        else:
            df["Lagerkostnad"] = 0

    if "Antall_lager" not in df.columns:
        if "Qty" in df.columns:
            df["Antall_lager"] = df["Qty"].apply(tekst_til_tall)
        elif "Antall" in df.columns:
            df["Antall_lager"] = df["Antall"].apply(tekst_til_tall)
        elif "Stock" in df.columns:
            df["Antall_lager"] = df["Stock"].apply(tekst_til_tall)
        else:
            df["Antall_lager"] = 0

    if "Name" not in df.columns:
        if "Produkt" in df.columns:
            df["Name"] = df["Produkt"]
        elif "Product" in df.columns:
            df["Name"] = df["Product"]
        elif "Produktnavn" in df.columns:
            df["Name"] = df["Produktnavn"]
        elif "Variant" in df.columns:
            df["Name"] = df["Variant"]
        else:
            df["Name"] = ""

    if "Color" not in df.columns:
        df["Color"] = ""

    if "Variant" not in df.columns:
        df["Variant"] = (df["Name"].astype(str) + " " + df["Color"].astype(str)).str.strip()

    if "Produktnøkkel" not in df.columns:
        if "Color" in df.columns:
            df["Produktnøkkel"] = (
                df["Name"].apply(normaliser_tekst)
                + " | "
                + df["Color"].apply(normaliser_tekst)
            )
        else:
            df["Produktnøkkel"] = df["Name"].apply(normaliser_tekst)

    if "Brand" not in df.columns:
        df["Brand"] = ""

    if "Group" not in df.columns:
        df["Group"] = ""

    if "Season" in df.columns:
        df["Sesongstype"] = df["Season"].apply(finn_sesongstype)
    elif "Sesongstype" not in df.columns:
        df["Sesongstype"] = "UKJENT"

    return df


def klargjor_salg(df):
    df = df.copy()

    if "Antall_solgt" not in df.columns:
        if "Qty" in df.columns:
            df["Antall_solgt"] = df["Qty"].apply(tekst_til_tall)
        elif "Antall" in df.columns:
            df["Antall_solgt"] = df["Antall"].apply(tekst_til_tall)
        else:
            df["Antall_solgt"] = 0

    if "Omsetning" not in df.columns:
        if "Price" in df.columns:
            df["Omsetning"] = df["Price"].apply(tekst_til_tall)
        elif "Brutto omsetning" in df.columns:
            df["Omsetning"] = df["Brutto omsetning"].apply(tekst_til_tall)
        elif "Gross Sales" in df.columns:
            df["Omsetning"] = df["Gross Sales"].apply(tekst_til_tall)
        else:
            df["Omsetning"] = 0

    if "Rabatt" not in df.columns:
        if "Discount" in df.columns:
            df["Rabatt"] = df["Discount"].apply(tekst_til_tall)
        else:
            df["Rabatt"] = 0

    if "Varekost_solgt" not in df.columns:
        if "Cost" in df.columns:
            df["Varekost_solgt"] = df["Cost"].apply(tekst_til_tall)
        else:
            df["Varekost_solgt"] = 0

    if "Bruttofortjeneste" not in df.columns:
        if "Gross Margin" in df.columns:
            df["Bruttofortjeneste"] = df["Gross Margin"].apply(tekst_til_tall)
        elif "Bruttomargin" in df.columns:
            df["Bruttofortjeneste"] = df["Bruttomargin"].apply(tekst_til_tall)
        else:
            df["Bruttofortjeneste"] = df["Omsetning"] - df["Varekost_solgt"]

    if "Produktnavn" not in df.columns:
        if "ReceiptLabel" in df.columns:
            df["Produktnavn"] = df["ReceiptLabel"]
        elif "PRODUCTID_FK" in df.columns:
            df["Produktnavn"] = df["PRODUCTID_FK"].apply(hent_produktnavn_fra_salg)
        elif "Product" in df.columns:
            df["Produktnavn"] = df["Product"]
        elif "Name" in df.columns:
            df["Produktnavn"] = df["Name"]
        elif "Variant" in df.columns:
            df["Produktnavn"] = df["Variant"]
        else:
            df["Produktnavn"] = ""

    if "Color" not in df.columns:
        df["Color"] = ""

    if "Variant" not in df.columns:
        df["Variant"] = (df["Produktnavn"].astype(str) + " " + df["Color"].astype(str)).str.strip()

    if "Produktnøkkel" not in df.columns:
        if "Color" in df.columns:
            df["Produktnøkkel"] = (
                df["Produktnavn"].apply(normaliser_tekst)
                + " | "
                + df["Color"].apply(normaliser_tekst)
            )
        else:
            df["Produktnøkkel"] = df["Produktnavn"].apply(normaliser_tekst)

    if "Subgroup" not in df.columns:
        df["Subgroup"] = ""

    if "Brand" not in df.columns:
        df["Brand"] = ""

    if "Group" not in df.columns:
        df["Group"] = ""

    df = df[df["Produktnøkkel"] != ""]

    return df


def vis_produkter_med_varianter(analyse):
    st.subheader("Produkter med farger/varianter")

    for col in [
        "Antall_lager",
        "Antall_solgt",
        "Lagerkostnad",
        "Omsetning",
        "Bruttofortjeneste",
    ]:
        if col not in analyse.columns:
            analyse[col] = 0

    if "Status" not in analyse.columns:
        analyse["Status"] = ""

    if "Sell-through %" not in analyse.columns:
        analyse["Sell-through %"] = 0

    if "Color" not in analyse.columns:
        analyse["Color"] = ""

    if "Variant" not in analyse.columns:
        analyse["Variant"] = analyse["Produkt"]

    produktliste = (
        analyse.groupby("Produkt")
        .agg(
            Antall_lager=("Antall_lager", "sum"),
            Antall_solgt=("Antall_solgt", "sum"),
            Lagerkostnad=("Lagerkostnad", "sum"),
            Omsetning=("Omsetning", "sum"),
            Bruttofortjeneste=("Bruttofortjeneste", "sum"),
        )
        .sort_values("Lagerkostnad", ascending=False)
        .reset_index()
    )

    for _, produkt_rad in produktliste.iterrows():
        produktnavn = produkt_rad["Produkt"]

        with st.expander(
            f"{produktnavn} | Lager: {int(produkt_rad['Antall_lager'])} | "
            f"Solgt: {int(produkt_rad['Antall_solgt'])} | "
            f"Lagerkostnad: {kr(produkt_rad['Lagerkostnad'])}"
        ):
            detaljer = analyse[analyse["Produkt"] == produktnavn].copy()

            kolonner = [
                "Variant",
                "Color",
                "Sesongstype",
                "Antall_lager",
                "Antall_solgt",
                "Lagerkostnad",
                "Omsetning",
                "Sell-through %",
                "Status",
            ]

            kolonner = [c for c in kolonner if c in detaljer.columns]

            st.dataframe(
                formater_tabell(detaljer[kolonner]),
                use_container_width=True,
            )


def analyser_lagerverdi(df):
    df = klargjor_lager(df)

    total_kostnad = df["Lagerkostnad"].sum()
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
        vis_produkter_med_varianter(df.rename(columns={"Name": "Produkt"}))

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
        if not produkt.empty:
            st.write(f"Produktet som binder mest kapital er **{produkt.index[0]}**.")
        if not merke.empty:
            st.write(f"Merket som binder mest kapital er **{merke.index[0]}**.")
        if not gruppe.empty:
            st.write(f"Varegruppen som binder mest kapital er **{gruppe.index[0]}**.")
        st.warning("Last også opp salgsrapport for å finne slow movers, fast movers og reorder-kandidater.")


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
            "Antall_solgt", "Omsetning", "Rabatt",
            "Varekost_solgt", "Bruttofortjeneste"
        ]]
        .sum()
        .sort_values("Omsetning", ascending=False)
    )

    produkt["Margin %"] = (
        produkt["Bruttofortjeneste"] / produkt["Omsetning"] * 100
    ).replace([float("inf")], 0).fillna(0).round(1)

    merke = (
        df.groupby("Brand")[[
            "Antall_solgt", "Omsetning", "Rabatt",
            "Varekost_solgt", "Bruttofortjeneste"
        ]]
        .sum()
        .sort_values("Omsetning", ascending=False)
    )

    merke["Margin %"] = (
        merke["Bruttofortjeneste"] / merke["Omsetning"] * 100
    ).replace([float("inf")], 0).fillna(0).round(1)

    gruppe = (
        df.groupby("Group")[[
            "Antall_solgt", "Omsetning", "Rabatt",
            "Varekost_solgt", "Bruttofortjeneste"
        ]]
        .sum()
        .sort_values("Omsetning", ascending=False)
    )

    gruppe["Margin %"] = (
        gruppe["Bruttofortjeneste"] / gruppe["Omsetning"] * 100
    ).replace([float("inf")], 0).fillna(0).round(1)

    undergruppe = (
        df.groupby("Subgroup")[[
            "Antall_solgt", "Omsetning", "Rabatt",
            "Varekost_solgt", "Bruttofortjeneste"
        ]]
        .sum()
        .sort_values("Omsetning", ascending=False)
    )

    undergruppe["Margin %"] = (
        undergruppe["Bruttofortjeneste"] / undergruppe["Omsetning"] * 100
    ).replace([float("inf")], 0).fillna(0).round(1)

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["Produkter/farger", "Merker", "Varegrupper", "Undergrupper", "Analyse"]
    )

    with tab1:
        st.subheader("Bestselgende produkter/farger")
        st.dataframe(formater_tabell(produkt.head(50)), use_container_width=True)
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
        st.subheader("Salg per undergruppe")
        st.dataframe(formater_tabell(undergruppe), use_container_width=True)
        st.bar_chart(undergruppe["Omsetning"].head(15))

    with tab5:
        st.success(f"Total omsetning er {kr(total_omsetning)}.")
        if not produkt.empty:
            st.write(f"Bestselgende produkt/farge er **{produkt.index[0]}**.")
        if not merke.empty:
            st.write(f"Sterkeste merke er **{merke.index[0]}**.")
        if not gruppe.empty:
            st.write(f"Sterkeste varegruppe er **{gruppe.index[0]}**.")
        if not undergruppe.empty:
            st.write(f"Sterkeste undergruppe er **{undergruppe.index[0]}**.")


def analyser_lager_og_salg(lager_df, salg_df):
    lager = klargjor_lager(lager_df)
    salg = klargjor_salg(salg_df)

    lager_produkt = lager.groupby("Produktnøkkel").agg(
        Produkt=("Name", "first"),
        Variant=("Variant", "first"),
        Color=("Color", "first"),
        Merke_lager=("Brand", "first"),
        Varegruppe_lager=("Group", "first"),
        Sesongstype=("Sesongstype", "first"),
        Antall_lager=("Antall_lager", "sum"),
        Lagerkostnad=("Lagerkostnad", "sum"),
    ).reset_index()

    salg_produkt = salg.groupby("Produktnøkkel").agg(
        Produkt_salg=("Produktnavn", "first"),
        Variant_salg=("Variant", "first"),
        Color_salg=("Color", "first"),
        Merke_salg=("Brand", "first"),
        Varegruppe_salg=("Group", "first"),
        Undergruppe_salg=("Subgroup", "first"),
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
    analyse["Variant"] = analyse["Variant"].fillna(analyse["Variant_salg"])
    analyse["Color"] = analyse["Color"].fillna(analyse["Color_salg"])
    analyse["Sesongstype"] = analyse["Sesongstype"].fillna("UKJENT")

    for c in [
        "Antall_lager", "Lagerkostnad", "Antall_solgt",
        "Omsetning", "Rabatt", "Bruttofortjeneste"
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
        sesonger_som_skal_vurderes = ["NOOS", "SS", "AW", "UKJENT"]
    else:
        sesonger_som_skal_vurderes = ["NOOS", valgt_sesong, "UKJENT"]

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
            | (analyse["Sesongstype"] == "UKJENT")
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

    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs(
        [
            "Oversikt",
            "Produkter",
            "Slow movers",
            "Reorder",
            "Sterke varer",
            "Sesong",
            "Undergrupper",
            "Analyse",
        ]
    )

    with tab1:
        vis = analyse.sort_values("Lagerkostnad", ascending=False)
        kolonner = [
            "Produkt", "Variant", "Color", "Sesongstype", "Antall_lager",
            "Antall_solgt", "Lagerkostnad", "Omsetning",
            "Bruttofortjeneste", "Sell-through %", "Margin %", "Status"
        ]
        kolonner = [c for c in kolonner if c in vis.columns]

        st.dataframe(
            formater_tabell(vis[kolonner].head(50)),
            use_container_width=True,
        )

    with tab2:
        vis_produkter_med_varianter(analyse)

    with tab3:
        slow = analyse[
            analyse["Status"].isin(["Slow mover", "Kritisk slow mover"])
        ].sort_values("Lagerkostnad", ascending=False)

        kolonner = [
            "Produkt", "Variant", "Color", "Sesongstype", "Antall_lager",
            "Antall_solgt", "Lagerkostnad", "Omsetning",
            "Sell-through %", "Status"
        ]
        kolonner = [c for c in kolonner if c in slow.columns]

        st.dataframe(
            formater_tabell(slow[kolonner]),
            use_container_width=True,
        )

    with tab4:
        reorder = analyse[
            analyse["Status"] == "Reorder-kandidat"
        ].sort_values("Antall_solgt", ascending=False)

        kolonner = [
            "Produkt", "Variant", "Color", "Sesongstype", "Antall_lager",
            "Antall_solgt", "Omsetning", "Bruttofortjeneste",
            "Sell-through %", "Status"
        ]
        kolonner = [c for c in kolonner if c in reorder.columns]

        st.dataframe(
            formater_tabell(reorder[kolonner]),
            use_container_width=True,
        )

    with tab5:
        sterke = analyse[
            analyse["Status"] == "Sterk vare"
        ].sort_values("Omsetning", ascending=False)

        kolonner = [
            "Produkt", "Variant", "Color", "Sesongstype", "Antall_lager",
            "Antall_solgt", "Omsetning", "Bruttofortjeneste",
            "Sell-through %", "Status"
        ]
        kolonner = [c for c in kolonner if c in sterke.columns]

        st.dataframe(
            formater_tabell(sterke[kolonner]),
            use_container_width=True,
        )

    with tab6:
        sesong = (
            analyse.groupby("Sesongstype")[[
                "Antall_lager", "Antall_solgt", "Lagerkostnad",
                "Omsetning", "Bruttofortjeneste"
            ]]
            .sum()
            .sort_values("Lagerkostnad", ascending=False)
        )

        st.subheader("Analyse per sesongstype")
        st.dataframe(formater_tabell(sesong), use_container_width=True)
        st.bar_chart(sesong["Lagerkostnad"])

    with tab7:
        if "Undergruppe_salg" in analyse.columns:
            undergruppe = (
                analyse.groupby("Undergruppe_salg")[[
                    "Antall_solgt", "Omsetning", "Bruttofortjeneste"
                ]]
                .sum()
                .sort_values("Omsetning", ascending=False)
            )

            st.subheader("Analyse per undergruppe")
            st.dataframe(formater_tabell(undergruppe), use_container_width=True)
            st.bar_chart(undergruppe["Omsetning"].head(15))
        else:
            st.info("Ingen undergruppe-data tilgjengelig.")

    with tab8:
        vis_ai_konsulent(
            analyse=analyse,
            total_lager=total_lager,
            total_salg=total_salg,
            total_fortjeneste=total_fortjeneste,
            valgt_sesong=valgt_sesong,
        )