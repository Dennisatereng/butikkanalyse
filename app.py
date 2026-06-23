import streamlit as st
import pandas as pd

st.set_page_config(page_title="Butikkanalyse", layout="wide")

st.title("Butikkanalyse")
st.caption("Last opp én eller flere salgsrapporter og få automatisk analyse.")


def les_csv(fil):
    encodings = ["utf-8-sig", "utf-8", "cp1252", "latin1"]

    for enc in encodings:
        try:
            fil.seek(0)
            df = pd.read_csv(fil, sep=";", encoding=enc)
            return df, enc
        except Exception:
            continue

    raise Exception("Kunne ikke lese CSV-filen.")


system = st.selectbox(
    "Velg system",
    ["Zedonk", "Front Systems", "Visma", "Annet"]
)

filer = st.file_uploader(
    "Last opp én eller flere CSV-filer",
    type=["csv"],
    accept_multiple_files=True
)

if filer:
    alle_data = []
    encodinger = []

    for fil in filer:
        df_fil, encoding_brukt = les_csv(fil)
        df_fil["Kilde_fil"] = fil.name
        alle_data.append(df_fil)
        encodinger.append(f"{fil.name}: {encoding_brukt}")

    df = pd.concat(alle_data, ignore_index=True)

    st.success(f"{len(filer)} fil(er) lest inn.")
    with st.expander("Vis filinfo"):
        st.write(encodinger)
        st.write(list(df.columns))
        st.dataframe(df.head(20))

    if st.button("Lag rapport", type="primary"):

        belop_kolonne = next(
            c for c in df.columns
            if "Sub Total (" in c
        )

        df["Beløp EUR"] = (
            df[belop_kolonne]
            .astype(str)
            .str.replace(" ", "", regex=False)
            .str.replace(".", "", regex=False)
            .str.replace(",", ".", regex=False)
            .astype(float)
        )

        kunde_rapport = (
            df.groupby("Customer")["Beløp EUR"]
            .sum()
            .sort_values(ascending=False)
            .to_frame()
        )

        kunde_rapport["Andel %"] = (
            kunde_rapport["Beløp EUR"]
            / kunde_rapport["Beløp EUR"].sum() * 100
        ).round(1)

        total = kunde_rapport["Beløp EUR"].sum()
        topp_1 = kunde_rapport.index[0]
        topp_5_andel = kunde_rapport["Andel %"].head(5).sum()
        topp_10_andel = kunde_rapport["Andel %"].head(10).sum()

        st.divider()

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total omsetning", f"€{total:,.0f}")
        col2.metric("Antall kunder", len(kunde_rapport))
        col3.metric("Største kunde", topp_1)
        col4.metric("Topp 10 andel", f"{topp_10_andel:.1f}%")

        st.subheader("Topp kunder")
        st.dataframe(kunde_rapport.head(30), use_container_width=True)

        st.subheader("Topp 10 kunder")
        st.bar_chart(kunde_rapport["Beløp EUR"].head(10))

        if "Season" in df.columns:
            sesong_rapport = (
                df.groupby("Season")["Beløp EUR"]
                .sum()
                .sort_values(ascending=False)
                .to_frame()
            )

            sesong_rapport["Andel %"] = (
                sesong_rapport["Beløp EUR"]
                / sesong_rapport["Beløp EUR"].sum() * 100
            ).round(1)

            st.subheader("Omsetning per sesong")
            st.dataframe(sesong_rapport, use_container_width=True)
            st.bar_chart(sesong_rapport["Beløp EUR"])

        if "Owner" in df.columns:
            selger_rapport = (
                df.groupby("Owner")["Beløp EUR"]
                .sum()
                .sort_values(ascending=False)
                .to_frame()
            )

            st.subheader("Omsetning per selger")
            st.dataframe(selger_rapport, use_container_width=True)

        st.subheader("Automatisk analyse")
        st.write(
            f"De fem største kundene står for **{topp_5_andel:.1f}%** av omsetningen."
        )
        st.write(
            f"De ti største kundene står for **{topp_10_andel:.1f}%** av omsetningen."
        )

        if topp_10_andel > 70:
            st.warning("Omsetningen er svært konsentrert rundt få kunder.")
        elif topp_10_andel > 50:
            st.info("Omsetningen er moderat konsentrert rundt toppkundene.")
        else:
            st.success("Kundeporteføljen virker relativt godt spredt.")