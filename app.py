import streamlit as st
import pandas as pd
import csv
import re

st.set_page_config(page_title="Butikkanalyse", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #f6f8fb; }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #08213d 0%, #0d2f55 100%);
    }

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] p {
        color: white !important;
    }

    section[data-testid="stSidebar"] .stSelectbox div,
    section[data-testid="stSidebar"] .stFileUploader div,
    section[data-testid="stSidebar"] input,
    section[data-testid="stSidebar"] button {
        color: #0f172a !important;
    }
</style>
""", unsafe_allow_html=True)


def kr(verdi):
    try:
        return f"{verdi:,.0f}".replace(",", " ") + " kr"
    except:
        return verdi


def eur(verdi):
    try:
        return f"€{verdi:,.0f}".replace(",", " ")
    except:
        return verdi


def tekst_til_tall(verdi):
    if pd.isna(verdi):
        return 0.0

    verdi = str(verdi)
    verdi = (
        verdi.replace("\xa0", "")
        .replace(" ", "")
        .replace("%", "")
        .replace(".", "")
        .replace(",", ".")
    )

    if verdi in ["", "-", "#Error", "nan"]:
        return 0.0

    try:
        return float(verdi)
    except:
        return 0.0


def normaliser_tekst(verdi):
    if pd.isna(verdi):
        return ""
    verdi = str(verdi).upper().strip()
    verdi = re.sub(r"\s+", " ", verdi)
    return verdi


def hent_produktnavn_fra_salg(verdi):
    if pd.isna(verdi):
        return ""

    tekst = str(verdi).strip()

    # Front bruker ofte: "PRODUKTNAVN  Farge"
    deler = re.split(r"\s{2,}", tekst)
    produktnavn = deler[0].strip()

    return produktnavn


def les_csv(fil):
    encodings = ["utf-8-sig", "utf-8", "cp1252", "latin1"]
    separators = [";", ","]

    for enc in encodings:
        for sep in separators:
            try:
                fil.seek(0)
                df = pd.read_csv(fil, sep=sep, encoding=enc)
                if len(df.columns) > 1:
                    return df, enc, sep
            except:
                continue

    raise Exception("Kunne ikke lese CSV-filen.")


def les_front_csv_rader(fil):
    encodings = ["utf-8-sig", "utf-8", "cp1252", "latin1"]

    for enc in encodings:
        try:
            fil.seek(0)
            tekst = fil.read().decode(enc)
            rader = list(csv.reader(tekst.splitlines(), delimiter=","))
            return rader, enc
        except:
            continue

    raise Exception("Kunne ikke lese Front-filen.")


def finn_rapporttype(df, filnavn=""):
    cols = set(df.columns)
    navn = filnavn.lower()

    if "dagsrapport" in navn:
        return "Front Dagsrapport"

    if {"Customer", "Season"}.issubset(cols) and any("Sub Total (" in c for c in df.columns):
        return "Zedonk Sales Orders"

    if {"StockName", "Season", "Brand", "Group", "Name", "Cost", "Qty"}.issubset(cols):
        return "Lagerverdi"

    if {"Brand", "Group", "PRODUCTID_FK", "Qty", "Price", "Discount", "Cost"}.issubset(cols):
        return "Front Salgsrapport"

    return "Ukjent"


def formater_tabell(df):
    df_vis = df.copy()

    for col in df_vis.columns:
        col_lav = col.lower()

        if any(ord in col_lav for ord in ["lagerkostnad", "kost", "omsetning", "salg", "rabatt", "fortjeneste"]):
            df_vis[col] = df_vis[col].apply(kr)

        elif "beløp" in col_lav:
            df_vis[col] = df_vis[col].apply(eur)

        elif "margin" in col_lav or "andel" in col_lav or "sell-through" in col_lav:
            df_vis[col] = df_vis[col].apply(lambda x: f"{x:.1f} %" if pd.notna(x) else "")

    return df_vis


def analyser_zedonk(df):
    belop_kolonne = next(c for c in df.columns if "Sub Total (" in c)

    df["Beløp EUR"] = (
        df[belop_kolonne]
        .astype(str)
        .str.replace(" ", "", regex=False)
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
        .astype(float)
    )

    kunder = (
        df.groupby("Customer")["Beløp EUR"]
        .sum()
        .sort_values(ascending=False)
        .to_frame()
    )

    kunder["Andel %"] = (
        kunder["Beløp EUR"] / kunder["Beløp EUR"].sum() * 100
    ).round(1)

    total = kunder["Beløp EUR"].sum()
    topp_10 = kunder["Andel %"].head(10).sum()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total omsetning", eur(total))
    col2.metric("Antall kunder", len(kunder))
    col3.metric("Største kunde", kunder.index[0])
    col4.metric("Topp 10 andel", f"{topp_10:.1f}%")

    tab1, tab2, tab3, tab4 = st.tabs(["Kunder", "Sesong", "Selger", "Analyse"])

    with tab1:
        st.subheader("Topp kunder")
        st.dataframe(kunder.head(30), use_container_width=True)
        st.bar_chart(kunder["Beløp EUR"].head(10))

    with tab2:
        if "Season" in df.columns:
            sesong = (
                df.groupby("Season")["Beløp EUR"]
                .sum()
                .sort_values(ascending=False)
                .to_frame()
            )
            sesong["Andel %"] = (
                sesong["Beløp EUR"] / sesong["Beløp EUR"].sum() * 100
            ).round(1)
            st.dataframe(sesong, use_container_width=True)
            st.bar_chart(sesong["Beløp EUR"])

    with tab3:
        if "Owner" in df.columns:
            selger = (
                df.groupby("Owner")["Beløp EUR"]
                .sum()
                .sort_values(ascending=False)
                .to_frame()
            )
            st.dataframe(selger, use_container_width=True)

    with tab4:
        st.info(f"De fem største kundene står for {kunder['Andel %'].head(5).sum():.1f}% av omsetningen.")
        st.info(f"De ti største kundene står for {topp_10:.1f}% av omsetningen.")

        if topp_10 > 70:
            st.warning("Omsetningen er svært konsentrert rundt få kunder.")
        elif topp_10 > 50:
            st.info("Omsetningen er moderat konsentrert rundt toppkundene.")
        else:
            st.success("Kundeporteføljen virker relativt godt spredt.")


def klargjor_lager(df):
    df = df.copy()

    df["Lagerkostnad"] = df["Cost"].apply(tekst_til_tall)
    df["Antall_lager"] = df["Qty"].apply(tekst_til_tall)
    df["Produktnøkkel"] = df["Name"].apply(normaliser_tekst)

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

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["Oversikt", "Produkter", "Merker", "Varegrupper", "Analyse"]
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
        st.subheader("Analyse og innsikt")
        st.success(f"Total lagerkostnad er {kr(total_kostnad)}.")
        st.write(f"Produktet som binder mest kapital er **{produkt.index[0]}**.")
        st.write(f"Merket som binder mest kapital er **{merke.index[0]}**.")
        st.write(f"Varegruppen som binder mest kapital er **{gruppe.index[0]}**.")
        st.warning(
            "Last også opp salgsrapport for å koble lager mot salg og finne slow movers, fast movers og reorder-kandidater."
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
        df.groupby("Produktnavn")[["Antall_solgt", "Omsetning", "Rabatt", "Varekost_solgt", "Bruttofortjeneste"]]
        .sum()
        .sort_values("Omsetning", ascending=False)
    )
    produkt["Margin %"] = (produkt["Bruttofortjeneste"] / produkt["Omsetning"] * 100).round(1)

    merke = (
        df.groupby("Brand")[["Antall_solgt", "Omsetning", "Rabatt", "Varekost_solgt", "Bruttofortjeneste"]]
        .sum()
        .sort_values("Omsetning", ascending=False)
    )
    merke["Margin %"] = (merke["Bruttofortjeneste"] / merke["Omsetning"] * 100).round(1)

    gruppe = (
        df.groupby("Group")[["Antall_solgt", "Omsetning", "Rabatt", "Varekost_solgt", "Bruttofortjeneste"]]
        .sum()
        .sort_values("Omsetning", ascending=False)
    )
    gruppe["Margin %"] = (gruppe["Bruttofortjeneste"] / gruppe["Omsetning"] * 100).round(1)

    tab1, tab2, tab3, tab4 = st.tabs(["Produkter", "Merker", "Varegrupper", "Analyse"])

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

    lager_produkt = (
        lager.groupby("Produktnøkkel")
        .agg(
            Produkt=("Name", "first"),
            Merke_lager=("Brand", "first"),
            Varegruppe_lager=("Group", "first"),
            Antall_lager=("Antall_lager", "sum"),
            Lagerkostnad=("Lagerkostnad", "sum"),
        )
        .reset_index()
    )

    salg_produkt = (
        salg.groupby("Produktnøkkel")
        .agg(
            Produkt_salg=("Produktnavn", "first"),
            Merke_salg=("Brand", "first"),
            Varegruppe_salg=("Group", "first"),
            Antall_solgt=("Antall_solgt", "sum"),
            Omsetning=("Omsetning", "sum"),
            Rabatt=("Rabatt", "sum"),
            Varekost_solgt=("Varekost_solgt", "sum"),
            Bruttofortjeneste=("Bruttofortjeneste", "sum"),
        )
        .reset_index()
    )

    analyse = pd.merge(lager_produkt, salg_produkt, on="Produktnøkkel", how="outer")

    analyse["Produkt"] = analyse["Produkt"].fillna(analyse["Produkt_salg"])
    analyse["Antall_lager"] = analyse["Antall_lager"].fillna(0)
    analyse["Lagerkostnad"] = analyse["Lagerkostnad"].fillna(0)
    analyse["Antall_solgt"] = analyse["Antall_solgt"].fillna(0)
    analyse["Omsetning"] = analyse["Omsetning"].fillna(0)
    analyse["Rabatt"] = analyse["Rabatt"].fillna(0)
    analyse["Bruttofortjeneste"] = analyse["Bruttofortjeneste"].fillna(0)

    analyse["Sell-through %"] = (
        analyse["Antall_solgt"] / (analyse["Antall_solgt"] + analyse["Antall_lager"]) * 100
    ).replace([float("inf")], 0).fillna(0).round(1)

    analyse["Margin %"] = (
        analyse["Bruttofortjeneste"] / analyse["Omsetning"] * 100
    ).replace([float("inf")], 0).fillna(0).round(1)

    analyse["Status"] = "Normal"

    analyse.loc[
        (analyse["Lagerkostnad"] > 0) & (analyse["Antall_solgt"] == 0),
        "Status"
    ] = "Kritisk slow mover"

    analyse.loc[
        (analyse["Lagerkostnad"] > 0) & (analyse["Sell-through %"] < 20) & (analyse["Antall_solgt"] > 0),
        "Status"
    ] = "Slow mover"

    analyse.loc[
        (analyse["Antall_lager"] <= 3) & (analyse["Antall_solgt"] >= 5),
        "Status"
    ] = "Reorder-kandidat"

    analyse.loc[
        (analyse["Sell-through %"] >= 70) & (analyse["Antall_lager"] > 0),
        "Status"
    ] = "Sterk vare"

    total_lager = analyse["Lagerkostnad"].sum()
    total_salg = analyse["Omsetning"].sum()
    total_fortjeneste = analyse["Bruttofortjeneste"].sum()
    slow_count = len(analyse[analyse["Status"].isin(["Slow mover", "Kritisk slow mover"])])

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Lagerkostnad", kr(total_lager))
    col2.metric("Omsetning", kr(total_salg))
    col3.metric("Bruttofortjeneste", kr(total_fortjeneste))
    col4.metric("Slow movers", slow_count)

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["Oversikt", "Slow movers", "Reorder", "Sterke varer", "Analyse"]
    )

    with tab1:
        st.subheader("Koblet lager og salg")
        vis = analyse.sort_values("Lagerkostnad", ascending=False)
        st.dataframe(
            formater_tabell(vis[[
                "Produkt",
                "Antall_lager",
                "Antall_solgt",
                "Lagerkostnad",
                "Omsetning",
                "Bruttofortjeneste",
                "Sell-through %",
                "Margin %",
                "Status",
            ]].head(50)),
            use_container_width=True
        )

    with tab2:
        st.subheader("Varer som binder kapital uten nok salg")
        slow = analyse[analyse["Status"].isin(["Slow mover", "Kritisk slow mover"])].sort_values("Lagerkostnad", ascending=False)
        st.dataframe(
            formater_tabell(slow[[
                "Produkt",
                "Antall_lager",
                "Antall_solgt",
                "Lagerkostnad",
                "Omsetning",
                "Sell-through %",
                "Status",
            ]]),
            use_container_width=True
        )

    with tab3:
        st.subheader("Mulige reorder-kandidater")
        reorder = analyse[analyse["Status"] == "Reorder-kandidat"].sort_values("Antall_solgt", ascending=False)
        st.dataframe(
            formater_tabell(reorder[[
                "Produkt",
                "Antall_lager",
                "Antall_solgt",
                "Omsetning",
                "Bruttofortjeneste",
                "Sell-through %",
                "Status",
            ]]),
            use_container_width=True
        )

    with tab4:
        st.subheader("Sterke varer")
        sterke = analyse[analyse["Status"] == "Sterk vare"].sort_values("Omsetning", ascending=False)
        st.dataframe(
            formater_tabell(sterke[[
                "Produkt",
                "Antall_lager",
                "Antall_solgt",
                "Omsetning",
                "Bruttofortjeneste",
                "Sell-through %",
                "Status",
            ]]),
            use_container_width=True
        )

    with tab5:
        st.subheader("Automatisk analyse")
        st.success(f"Lageret binder {kr(total_lager)} i kost.")
        st.info(f"Salgsrapporten viser {kr(total_salg)} i omsetning.")
        st.write(f"Det er **{slow_count}** produkter som bør vurderes som slow movers.")

        if slow_count > 0:
            topp_slow = analyse[analyse["Status"].isin(["Slow mover", "Kritisk slow mover"])].sort_values("Lagerkostnad", ascending=False).iloc[0]
            st.warning(
                f"Viktigste slow mover er **{topp_slow['Produkt']}**, som binder {kr(topp_slow['Lagerkostnad'])}."
            )

        reorder_count = len(analyse[analyse["Status"] == "Reorder-kandidat"])
        if reorder_count > 0:
            st.success(f"Det finnes **{reorder_count}** mulige reorder-kandidater.")
        else:
            st.info("Ingen tydelige reorder-kandidater funnet basert på dagens regler.")


def hent_front_seksjon(rader, startkode):
    for i, rad in enumerate(rader):
        if len(rad) > 0 and rad[0] == startkode:
            data = []
            j = i + 1

            while j < len(rader):
                neste = rader[j]

                if len(neste) == 0:
                    break

                if len(neste) > 0 and str(neste[0]).startswith("ColValue"):
                    break

                if len(neste) >= 3:
                    data.append({
                        "Navn": neste[0],
                        "Antall": tekst_til_tall(neste[1]),
                        "Omsetning": tekst_til_tall(neste[2]),
                        "Netto": tekst_til_tall(neste[3]) if len(neste) > 3 else 0,
                    })

                j += 1

            return pd.DataFrame(data)

    return pd.DataFrame()


def analyser_front_dagsrapport(fil):
    rader, encoding = les_front_csv_rader(fil)

    dato = ""
    butikk = ""
    total_omsetning = 0
    total_antall = 0

    if len(rader) > 1:
        dato = rader[1][0].replace("Dagsrapport ", "")

    for rad in rader:
        if len(rad) > 2 and "JOHNNYLOVE" in str(rad[0]).upper():
            butikk = rad[0]
            total_antall = tekst_til_tall(rad[1])
            total_omsetning = tekst_til_tall(rad[2])
            break

    selgere = hent_front_seksjon(rader, "ColValue5")
    dame_herre = hent_front_seksjon(rader, "ColValue4")
    varegrupper = hent_front_seksjon(rader, "ColValue2")
    merke = hent_front_seksjon(rader, "ColValue")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Butikk", butikk)
    col2.metric("Dato", dato)
    col3.metric("Omsetning", kr(total_omsetning))
    col4.metric("Antall", f"{total_antall:,.0f}".replace(",", " "))

    tab1, tab2, tab3, tab4 = st.tabs(["Selgere", "Dame/Herre", "Varegrupper", "Merker"])

    with tab1:
        if not selgere.empty:
            selgere = selgere.sort_values("Omsetning", ascending=False)
            st.dataframe(formater_tabell(selgere), use_container_width=True)
            st.bar_chart(selgere.set_index("Navn")["Omsetning"])

    with tab2:
        if not dame_herre.empty:
            dame_herre = dame_herre.sort_values("Omsetning", ascending=False)
            st.dataframe(formater_tabell(dame_herre), use_container_width=True)

    with tab3:
        if not varegrupper.empty:
            varegrupper = varegrupper.sort_values("Omsetning", ascending=False)
            st.dataframe(formater_tabell(varegrupper), use_container_width=True)

    with tab4:
        if not merke.empty:
            merke = merke.sort_values("Omsetning", ascending=False)
            st.dataframe(formater_tabell(merke), use_container_width=True)


st.sidebar.title("Butikkanalyse")
st.sidebar.caption("Data som gir bedre beslutninger")

system = st.sidebar.selectbox(
    "Velg system",
    ["Automatisk", "Zedonk", "Front Systems", "Shopify", "Visma", "Annet"]
)

filer = st.sidebar.file_uploader(
    "Last opp CSV-filer",
    type=["csv"],
    accept_multiple_files=True
)

st.sidebar.divider()

if not filer:
    st.info("Last opp salgsrapporter og/eller lagerrapporter i menyen til venstre.")
else:
    st.sidebar.write("Filer lastet opp:")
    for f in filer:
        st.sidebar.write(f"• {f.name}")

    lager_dfs = []
    salg_dfs = []
    zedonk_dfs = []
    front_dagsrapporter = []
    ukjent_dfs = []
    filinfo = []

    for fil in filer:
        if "dagsrapport" in fil.name.lower() or system == "Front Systems":
            front_dagsrapporter.append(fil)
            filinfo.append(f"{fil.name} | Front dagsrapport")
            continue

        df_fil, enc, sep = les_csv(fil)
        rapporttype = finn_rapporttype(df_fil, fil.name)
        df_fil["Kilde_fil"] = fil.name

        filinfo.append(f"{fil.name} | {rapporttype} | {enc} | sep: {sep}")

        if rapporttype == "Lagerverdi":
            lager_dfs.append(df_fil)
        elif rapporttype == "Front Salgsrapport":
            salg_dfs.append(df_fil)
        elif rapporttype == "Zedonk Sales Orders":
            zedonk_dfs.append(df_fil)
        else:
            ukjent_dfs.append(df_fil)

    with st.expander("Rådata og filinfo"):
        st.write(filinfo)

    if st.button("Lag rapport", type="primary"):

        if lager_dfs and salg_dfs:
            st.success("Rapporttype oppdaget: Lager + salg")
            lager_df = pd.concat(lager_dfs, ignore_index=True)
            salg_df = pd.concat(salg_dfs, ignore_index=True)
            analyser_lager_og_salg(lager_df, salg_df)

        elif lager_dfs:
            st.success("Rapporttype oppdaget: Lagerverdi")
            lager_df = pd.concat(lager_dfs, ignore_index=True)
            analyser_lagerverdi(lager_df)

        elif salg_dfs:
            st.success("Rapporttype oppdaget: Front salgsrapport")
            salg_df = pd.concat(salg_dfs, ignore_index=True)
            analyser_front_salg(salg_df)

        elif zedonk_dfs:
            st.success("Rapporttype oppdaget: Zedonk Sales Orders")
            zedonk_df = pd.concat(zedonk_dfs, ignore_index=True)
            analyser_zedonk(zedonk_df)

        elif front_dagsrapporter:
            st.success("Rapporttype oppdaget: Front Dagsrapport")
            analyser_front_dagsrapport(front_dagsrapporter[0])

        else:
            st.error("Ukjent rapporttype. Systemet vet ikke ennå hvordan denne filen skal analyseres.")