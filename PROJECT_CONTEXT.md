# PROJECT_CONTEXT.md

# Butikkanalyse – Prosjektbeskrivelse

## Mål

Målet er å bygge en SaaS-plattform som hjelper butikker med å analysere lager- og salgsdata.

Løsningen skal gi innsikt som normalt krever en erfaren retail-konsulent.

Systemet skal være enkelt å bruke:

1. Kunden velger hvilket system rapportene kommer fra.
2. Kunden laster opp CSV-filer.
3. Systemet analyserer rapportene.
4. Kunden får KPI-er, grafer, anbefalinger og AI-genererte tiltak.

På sikt skal kunden kunne logge inn og se historiske analyser over tid.

---

# Visjon

Plattformen skal kunne brukes av:

- enkeltbutikker
- butikkjeder
- grossister
- konsulenter

Systemet skal støtte mange ERP- og POS-systemer uten at analyselogikken må skrives om.

---

# Teknologi

Frontend:
- Streamlit

Backend:
- Python

Data:
- Pandas

Fremtidig AI:
- OpenAI API

---

# Prosjektstruktur

app.py
- Hovedapplikasjon
- Filopplasting
- Navigasjon
- Starter analyser

modules/

helpers.py
- Felles hjelpefunksjoner
- CSV-lesing
- Tallkonvertering
- Formatering

guides.py
- Steg-for-steg veiledninger
- Hvordan hente rapporter fra hvert system

front.py
- Front Systems
- Dagsrapport

lager.py
- Lageranalyse
- Salgsanalyse
- Sell-through
- Slow movers
- Reorder
- AW/SS/NOOS

zedonk.py
- Analyse av Zedonk Sales Orders

---

# Implementert

## Front Systems

✓ Lagerverdi

✓ Salgsrapport

✓ Dagsrapport

---

## Lageranalyse

✓ Lagerkostnad

✓ Kapitalbinding

✓ Produkter

✓ Merker

✓ Varegrupper

✓ Sell-through

✓ Bruttomargin

✓ Slow movers

✓ Reorder-kandidater

✓ Sterke varer

✓ AW

✓ SS

✓ NOOS

---

## Zedonk

✓ Sales Orders

✓ Kundeanalyse

✓ Sesonganalyse

---

# Regler

## app.py

Skal være så liten som mulig.

Kun:

- brukergrensesnitt
- filopplasting
- routing
- starte analyser

Ingen analysekode skal ligge her.

---

## modules

Ny funksjonalitet legges i egne filer.

Eksempel:

visma.py

shopify.py

ai_analysis.py

dashboard.py

pdf_export.py

osv.

---

# Sesonglogikk

NOOS analyseres alltid.

Når brukeren velger:

SS

skal analysen vise:

SS + NOOS

Når brukeren velger:

AW

skal analysen vise:

AW + NOOS

AW skal aldri markeres som slow movers midt på sommeren.

SS skal aldri markeres som slow movers midt på vinteren.

---

# Fremtidige funksjoner

## AI

AI skal analysere rapportene og gi konkrete anbefalinger.

Eksempler:

- hvilke varer bør kjøpes inn
- hvilke varer bør settes på kampanje
- hvilke varer binder unødvendig kapital
- hvilke merker presterer dårlig
- hvilke varegrupper vokser
- hvilke produkter bør fases ut

---

## Dashboard

- KPI-kort
- Grafer
- Trender
- Historikk

---

## Kundeportal

Kunden skal kunne:

- logge inn
- laste opp rapporter
- lagre historikk
- sammenligne måneder
- laste ned PDF
- se AI-anbefalinger

---

## Konsulentportal

Konsulenter skal kunne:

- administrere flere kunder
- sammenligne butikker
- se benchmark
- eksportere rapporter
- skrive egne kommentarer

---

# Viktige prinsipper

- Ikke bryt eksisterende funksjonalitet.
- Gjør små endringer av gangen.
- Hold koden modulær.
- Ikke legg analysekode i app.py.
- Forklar hvilke filer som endres før nye funksjoner implementeres.
- Gjenbruk eksisterende funksjoner der det er mulig.

---

# Langsiktig mål

Plattformen skal bli den mest komplette analyseplattformen for retail i Norden.