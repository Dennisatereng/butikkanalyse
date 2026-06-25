# Butikkanalyse

En Streamlit-basert analyseplattform for butikker.

Prosjektet analyserer lager- og salgsdata fra ulike butikk- og ERP-systemer, og gir innsikt i blant annet:

- Lagerverdi
- Kapitalbinding
- Slow movers
- Fast movers
- Sell-through
- Reorder-kandidater
- Bruttomargin
- Sesonganalyse (AW / SS / NOOS)
- AI-baserte anbefalinger (kommer)

---

## Støttede systemer

### Ferdig

- Front Systems
    - Lagerverdi
    - Salgsrapport
    - Dagsrapport

- Zedonk
    - Sales Orders

### Planlagt

- Visma
- DDD
- Shopify
- Unipos
- Flere ERP-systemer

---

## Prosjektstruktur

```
app.py                 # Hovedapplikasjon

modules/
    helpers.py         # Felles hjelpefunksjoner
    guides.py          # Veiledninger for rapporter
    front.py           # Front Systems
    lager.py           # Lager- og salgsanalyse
    zedonk.py          # Zedonk-analyse
```

---

## Installasjon

Opprett virtuelt miljø

```bash
python -m venv .venv
```

Aktiver miljø

Windows

```bash
.venv\Scripts\activate
```

Mac/Linux

```bash
source .venv/bin/activate
```

Installer pakker

```bash
pip install -r requirements.txt
```

---

## Starte prosjektet

```bash
streamlit run app.py
```

---

## Hvordan bruke

1. Velg butikk-/ERP-system.
2. Last opp én eller flere CSV-filer.
3. Trykk **Lag rapport**.
4. Se analyse og KPI-er.

---

## Utviklingsprinsipper

- Prosjektet skal være modulært.
- Ny funksjonalitet legges i `modules/`.
- `app.py` skal kun styre brukergrensesnitt og flyt.
- Eksisterende funksjonalitet skal ikke brytes ved nye endringer.

---

## Kommende funksjoner

- AI-analyse med konkrete anbefalinger
- PDF-rapport
- Benchmark mellom butikker
- Historikk over tid
- Dashboard
- Kundeportal
- Konsulentportal
- Automatisk import fra ERP-systemer

---

## Lisens

Privat prosjekt.