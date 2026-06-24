import streamlit as st
import pandas as pd
import csv

from modules.helpers import *


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

    tab1, tab2, tab3, tab4 = st.tabs(
        ["Selgere", "Dame/Herre", "Varegrupper", "Merker"]
    )

    with tab1:
        if not selgere.empty:
            selgere = selgere.sort_values(
                "Omsetning",
                ascending=False
            )

            st.dataframe(
                formater_tabell(selgere),
                use_container_width=True
            )

            st.bar_chart(
                selgere.set_index("Navn")["Omsetning"]
            )

    with tab2:
        if not dame_herre.empty:
            dame_herre = dame_herre.sort_values(
                "Omsetning",
                ascending=False
            )

            st.dataframe(
                formater_tabell(dame_herre),
                use_container_width=True
            )

    with tab3:
        if not varegrupper.empty:
            varegrupper = varegrupper.sort_values(
                "Omsetning",
                ascending=False
            )

            st.dataframe(
                formater_tabell(varegrupper),
                use_container_width=True
            )

    with tab4:
        if not merke.empty:
            merke = merke.sort_values(
                "Omsetning",
                ascending=False
            )

            st.dataframe(
                formater_tabell(merke),
                use_container_width=True
            )