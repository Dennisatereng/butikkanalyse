import pandas as pd
import re


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

    if verdi in ["", "-", "#Error", "nan", "None"]:
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
    deler = re.split(r"\s{2,}", tekst)

    return deler[0].strip()


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


def les_excel(fil):
    try:
        fil.seek(0)
        df = pd.read_excel(fil)

        return df, "excel", "xlsx"

    except Exception as e:
        raise Exception(f"Kunne ikke lese Excel-filen: {e}")


def les_fil(fil):
    filnavn = fil.name.lower()

    if filnavn.endswith(".xlsx") or filnavn.endswith(".xls"):
        return les_excel(fil)

    return les_csv(fil)


def formater_tabell(df):
    df_vis = df.copy()

    for col in df_vis.columns:
        col_lav = col.lower()

        if any(
            ord in col_lav
            for ord in [
                "lagerkostnad",
                "kost",
                "omsetning",
                "salg",
                "rabatt",
                "fortjeneste",
                "brutto",
                "marginbeløp",
            ]
        ):
            df_vis[col] = df_vis[col].apply(kr)

        elif "beløp" in col_lav:
            df_vis[col] = df_vis[col].apply(eur)

        elif (
            "margin" in col_lav
            or "andel" in col_lav
            or "sell-through" in col_lav
            or "dg" in col_lav
        ):
            df_vis[col] = df_vis[col].apply(
                lambda x: f"{x:.1f} %" if pd.notna(x) else ""
            )

    return df_vis