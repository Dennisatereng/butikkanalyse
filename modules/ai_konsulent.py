import streamlit as st

from modules.helpers import *


def vis_ai_konsulent(analyse, total_lager, total_salg, total_fortjeneste, valgt_sesong):
    st.subheader("AI-butikkonsulent")

    slow = analyse[
        analyse["Status"].isin(["Slow mover", "Kritisk slow mover"])
    ].sort_values("Lagerkostnad", ascending=False)

    reorder = analyse[
        analyse["Status"] == "Reorder-kandidat"
    ].sort_values("Antall_solgt", ascending=False)

    sterke = analyse[
        analyse["Status"] == "Sterk vare"
    ].sort_values("Omsetning", ascending=False)

    slow_kapital = slow["Lagerkostnad"].sum()
    mulig_frigjort = slow.head(20)["Lagerkostnad"].sum()

    col1, col2, col3 = st.columns(3)
    col1.metric("Kapital i slow movers", kr(slow_kapital))
    col2.metric("Kan frigjøres først", kr(mulig_frigjort))
    col3.metric("Reorder-kandidater", len(reorder))

    st.markdown("### Kritiske funn")

    if slow.empty:
        st.success("Ingen kritiske slow movers funnet i valgt sesong.")
    else:
        kritiske = slow.head(10).copy()
        kritiske["Foreslått tiltak"] = kritiske.apply(_foresla_tiltak, axis=1)

        st.dataframe(
            formater_tabell(
                kritiske[
                    [
                        "Produkt",
                        "Sesongstype",
                        "Antall_lager",
                        "Antall_solgt",
                        "Lagerkostnad",
                        "Omsetning",
                        "Sell-through %",
                        "Status",
                        "Foreslått tiltak",
                    ]
                ]
            ),
            use_container_width=True,
        )

    st.markdown("### Kapital som kan frigjøres")

    if slow_kapital > 0:
        st.info(
            f"Slow movers binder totalt **{kr(slow_kapital)}** i lagerkostnad. "
            f"De 20 største slow moverne alene binder **{kr(mulig_frigjort)}**."
        )

        høy = slow[slow["Lagerkostnad"] >= 20000]["Lagerkostnad"].sum()
        medium = slow[
            (slow["Lagerkostnad"] >= 5000)
            & (slow["Lagerkostnad"] < 20000)
        ]["Lagerkostnad"].sum()
        lav = slow[slow["Lagerkostnad"] < 5000]["Lagerkostnad"].sum()

        kapital_tabell = {
            "Prioritet": ["Høy", "Medium", "Lav"],
            "Kapital bundet": [høy, medium, lav],
            "Tiltak": [
                "Kampanje / tydelig eksponering",
                "Følg opp og vurder rabatt",
                "Overvåk eller flytt til outlet",
            ],
        }

        st.dataframe(
            formater_tabell(__import__("pandas").DataFrame(kapital_tabell)),
            use_container_width=True,
        )
    else:
        st.success("Ingen vesentlig kapital bundet i slow movers.")

    st.markdown("### AI-anbefalinger")

    anbefalinger = _lag_anbefalinger(
        analyse=analyse,
        slow=slow,
        reorder=reorder,
        sterke=sterke,
        total_lager=total_lager,
        total_salg=total_salg,
        valgt_sesong=valgt_sesong,
    )

    for i, anbefaling in enumerate(anbefalinger, start=1):
        st.write(f"**{i}. {anbefaling}**")

    st.markdown("### Hva bør gjøres denne uka?")

    tiltak = _lag_ukesplan(slow, reorder, sterke)

    for i, punkt in enumerate(tiltak, start=1):
        st.write(f"{i}. {punkt}")

    st.markdown("### Simulering: kampanje på slow movers")

    if slow.empty:
        st.info("Ingen slow movers å simulere kampanje på.")
    else:
        rabatt = st.slider(
            "Velg rabattnivå",
            min_value=10,
            max_value=70,
            value=30,
            step=5,
        )

        antatt_andel_solgt = min(0.15 + rabatt / 100, 0.85)
        estimert_frigjort = slow_kapital * antatt_andel_solgt
        estimert_omsetning = estimert_frigjort * (1 - rabatt / 100)

        c1, c2, c3 = st.columns(3)
        c1.metric("Rabatt", f"{rabatt}%")
        c2.metric("Estimert frigjort kapital", kr(estimert_frigjort))
        c3.metric("Estimert kontantstrøm", kr(estimert_omsetning))

        st.caption(
            "Dette er en enkel simulering basert på lagerkostnad, rabatt og antatt salgseffekt. "
            "Senere kan denne modellen forbedres med historiske salgsdata."
        )


def _foresla_tiltak(rad):
    if rad["Lagerkostnad"] >= 20000 and rad["Antall_solgt"] == 0:
        return "Prioriter kampanje / flytt til bedre eksponering"

    if rad["Lagerkostnad"] >= 20000:
        return "Kampanje eller redusert neste innkjøp"

    if rad["Sell-through %"] < 10:
        return "Vurder rabatt eller outlet"

    return "Følg opp i neste periode"


def _lag_anbefalinger(analyse, slow, reorder, sterke, total_lager, total_salg, valgt_sesong):
    anbefalinger = []

    if not slow.empty:
        anbefalinger.append(
            f"Start med de {min(len(slow), 20)} største slow moverne. "
            f"De binder {kr(slow.head(20)['Lagerkostnad'].sum())} i kapital."
        )

    if not reorder.empty:
        anbefalinger.append(
            f"Vurder reorder på {len(reorder)} produkter med lav lagerbeholdning og godt salg."
        )

    if not sterke.empty:
        topp = sterke.iloc[0]
        anbefalinger.append(
            f"Følg opp sterke varer som {topp['Produkt']}. Den har høy sell-through og fortsatt lager."
        )

    if total_lager > 0 and total_salg > 0:
        forhold = total_lager / total_salg

        if forhold > 0.8:
            anbefalinger.append(
                "Lagerbindingen virker høy sammenlignet med salget. Vurder å redusere innkjøp i svake varegrupper."
            )
        else:
            anbefalinger.append(
                "Forholdet mellom lager og salg virker relativt sunt i valgt periode."
            )

    if valgt_sesong in ["SS", "AW"]:
        anbefalinger.append(
            f"Du analyserer {valgt_sesong}. NOOS er inkludert, men sesongvarer bør vurderes ut fra riktig salgsvindu."
        )

    if not anbefalinger:
        anbefalinger.append("Ingen tydelige avvik funnet i valgt analyse.")

    return anbefalinger


def _lag_ukesplan(slow, reorder, sterke):
    tiltak = []

    if not slow.empty:
        tiltak.append(
            f"Gå gjennom de 10 største slow moverne og bestem kampanje, flytting eller utfasing."
        )

    if not reorder.empty:
        tiltak.append(
            f"Sjekk reorder på de {min(len(reorder), 10)} mest solgte produktene med lav beholdning."
        )

    if not sterke.empty:
        tiltak.append(
            "Sikre at de sterkeste varene er godt eksponert i butikk og på nett."
        )

    tiltak.append("Sammenlign funnene med neste rapport for å se om tiltakene virker.")

    return tiltak