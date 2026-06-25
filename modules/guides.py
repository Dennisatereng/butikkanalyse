import streamlit as st

GUIDER = {
    "Front Systems": {
        "tittel": "Front Systems",
        "beskrivelse": "Anbefalt oppsett for butikkrapportering, lageranalyse og salgsanalyse.",
        "rapporter": [
            {
                "navn": "Lagerverdi pr. lager",
                "brukes_til": "Lagerkostnad, kapitalbinding, varer som binder mest kapital, merker, varegrupper og sesonger.",
                "steg": [
                    "Gå til Rapporter i Front",
                    "Velg Lager",
                    "Velg Lagerverdi pr. lager",
                    "Velg riktig butikk/lager",
                    "Eksporter som CSV",
                    "Last opp filen her",
                ],
            },
            {
                "navn": "Salg pr. varegruppe / undergruppe pr. butikk",
                "brukes_til": "Kobles mot lagerrapporten for å beregne sell-through, slow movers, reorder-kandidater, marginer, farger/varianter og AI-analyse.",
                "steg": [
                    "Gå til Rapporter i Front",
                    "Velg Salg",
                    "Velg 'Salg pr. varegruppe / undergruppe pr. butikk'",
                    "Velg ønsket butikk",
                    "Velg ønsket periode",
                    "Eksporter som CSV",
                    "Last opp filen sammen med 'Lagerverdi pr. lager'",
                ],
            },
            {
                "navn": "Dagsrapport",
                "brukes_til": "Daglig omsetning, selgere, varegrupper, dame/herre og merker.",
                "steg": [
                    "Gå til Rapporter i Front",
                    "Velg Dagsrapport",
                    "Velg ønsket dato",
                    "Eksporter som CSV",
                    "Last opp filen her",
                ],
            },
        ],
        "best": "Lagerverdi pr. lager + Salg pr. varegruppe / undergruppe pr. butikk gir best analyse. Dagsrapport kan lastes opp alene for rask dagsanalyse.",
    },

    "Zedonk": {
        "tittel": "Zedonk",
        "beskrivelse": "Anbefalt oppsett for wholesale, kunder, sesonger og ordreanalyse.",
        "rapporter": [
            {
                "navn": "Sales Orders",
                "brukes_til": "Kundeanalyse, sesonger, omsetning, land, ordre og wholesale-status.",
                "steg": [
                    "Gå til Sales Orders i Zedonk",
                    "Filtrer ønsket sesong eller periode",
                    "Eksporter som CSV",
                    "Last opp én eller flere Sales Orders-filer her",
                ],
            },
            {
                "navn": "Inventory / Stock",
                "brukes_til": "Lagerbeholdning og kapitalbinding i wholesale.",
                "steg": [
                    "Gå til Inventory eller Stock",
                    "Velg ønsket lager eller sesong",
                    "Eksporter som CSV",
                    "Last opp sammen med salgsdata når tilgjengelig",
                ],
            },
        ],
        "best": "Sales Orders gir god kunde-, sesong- og wholesaleanalyse.",
    },

    "Visma": {
        "tittel": "Visma",
        "beskrivelse": "Foreløpig veiledning. Må tilpasses etter hvilken Visma-løsning kunden bruker.",
        "rapporter": [
            {
                "navn": "Varelager",
                "brukes_til": "Lagerverdi, antall på lager og kapitalbinding.",
                "steg": [
                    "Finn rapport for varelager",
                    "Eksporter varenummer, antall, kostpris og salgspris",
                    "Lagre som CSV eller Excel",
                    "Last opp filen her",
                ],
            },
            {
                "navn": "Salgstransaksjoner",
                "brukes_til": "Solgte varer, omsetning, margin og perioder.",
                "steg": [
                    "Finn rapport for salg eller fakturalinjer",
                    "Eksporter varenummer, antall solgt, dato og beløp",
                    "Last opp sammen med varelager",
                ],
            },
        ],
        "best": "Last opp både varelager og salgstransaksjoner hvis mulig.",
    },

    "Shopify": {
        "tittel": "Shopify",
        "beskrivelse": "Anbefalt oppsett for nettbutikkdata.",
        "rapporter": [
            {
                "navn": "Orders export",
                "brukes_til": "Omsetning, kunder, produkter og ordre.",
                "steg": [
                    "Gå til Orders i Shopify",
                    "Velg ønsket periode",
                    "Eksporter ordre som CSV",
                    "Last opp filen her",
                ],
            },
            {
                "navn": "Products export",
                "brukes_til": "Produkter, varianter, størrelser, farger og lager.",
                "steg": [
                    "Gå til Products i Shopify",
                    "Eksporter produkter som CSV",
                    "Last opp sammen med ordredata",
                ],
            },
        ],
        "best": "Orders + Products gir best analyse av salg, lager og varianter.",
    },

    "DDD": {
        "tittel": "DDD",
        "beskrivelse": "Foreløpig plassholder. Her legges riktig eksportveiledning inn når rapportene er kartlagt.",
        "rapporter": [
            {
                "navn": "Salgsrapport",
                "brukes_til": "Omsetning, varer og perioder.",
                "steg": [
                    "Finn salgsrapport i DDD",
                    "Eksporter varenummer, antall solgt og omsetning",
                    "Last opp filen her",
                ],
            },
            {
                "navn": "Lagerrapport",
                "brukes_til": "Lagerverdi, beholdning og slow movers.",
                "steg": [
                    "Finn lagerrapport i DDD",
                    "Eksporter varenummer, antall og kostpris",
                    "Last opp sammen med salgsrapport",
                ],
            },
        ],
        "best": "Last opp både lagerrapport og salgsrapport hvis mulig.",
    },
}


def vis_startside(system):
    st.title("Butikkanalyse")
    st.caption("Velg system til venstre, finn riktige rapporter og last dem opp for analyse.")

    if system == "Automatisk":
        st.info("Velg system i menyen til venstre for å se anbefalte rapporter og steg-for-steg veiledning.")
        return

    if system not in GUIDER:
        st.warning("Det finnes ikke egen veiledning for dette systemet ennå.")
        return

    guide = GUIDER[system]

    st.subheader(f"Veiledning for {guide['tittel']}")
    st.write(guide["beskrivelse"])

    st.markdown("### Anbefalte rapporter")

    for i, rapport in enumerate(guide["rapporter"], start=1):
        with st.expander(f"{i}. {rapport['navn']}", expanded=i == 1):
            st.write(f"**Brukes til:** {rapport['brukes_til']}")
            st.markdown("**Slik finner du rapporten:**")

            for nr, steg in enumerate(rapport["steg"], start=1):
                st.write(f"{nr}. {steg}")

    st.divider()
    st.markdown("### Beste analyse får du ved å laste opp")
    st.success(guide["best"])