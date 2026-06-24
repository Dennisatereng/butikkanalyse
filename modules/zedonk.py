import streamlit as st

from modules.helpers import *


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

    tab1, tab2, tab3, tab4 = st.tabs(
        ["Kunder", "Sesong", "Selger", "Analyse"]
    )

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
                sesong["Beløp EUR"]
                / sesong["Beløp EUR"].sum()
                * 100
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
        st.info(
            f"De fem største kundene står for "
            f"{kunder['Andel %'].head(5).sum():.1f}% av omsetningen."
        )

        st.info(
            f"De ti største kundene står for "
            f"{topp_10:.1f}% av omsetningen."
        )