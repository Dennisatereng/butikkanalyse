import pandas as pd
import re


def normaliser_variantnavn(verdi):
    if pd.isna(verdi):
        return ""

    tekst = str(verdi).strip()
    tekst = re.sub(r"\s+", " ", tekst)
    tekst = tekst.replace(" Total", "").strip()

    return tekst


def lag_variantnokkel(produkt, farge):
    produkt = normaliser_variantnavn(produkt).upper()
    farge = normaliser_variantnavn(farge).upper()

    return f"{produkt} | {farge}"


def les_front_stock_excel(fil):
    fil.seek(0)
    raw = pd.read_excel(fil, sheet_name=0, header=None)

    rader = []

    current_season = ""
    current_brand = ""
    current_group = ""
    current_product = ""

    for _, row in raw.iterrows():
        col0 = row[0] if 0 in row.index else None
        col1 = row[1] if 1 in row.index else None
        col2 = row[2] if 2 in row.index else None
        col3 = row[3] if 3 in row.index else None
        col5 = row[5] if 5 in row.index else None
        stock_value = row[7] if 7 in row.index else 0
        stock_qty = row[8] if 8 in row.index else 0

        if pd.notna(col0):
            tekst = str(col0).strip()
            if tekst not in ["Grand Total"] and not tekst.endswith("Total"):
                current_season = tekst

        if pd.notna(col1):
            tekst = str(col1).strip()
            if tekst.endswith("Total"):
                current_brand = tekst.replace(" Total", "").strip()
            elif tekst not in ["Grand Total"]:
                current_brand = tekst

        if pd.notna(col2):
            tekst = str(col2).strip()
            if tekst.endswith("Total"):
                current_group = tekst.replace(" Total", "").strip()
            elif tekst not in ["Grand Total"]:
                current_group = tekst

        if pd.notna(col3):
            tekst = str(col3).strip()
            if tekst.endswith("Total"):
                current_product = tekst.replace(" Total", "").strip()
            elif tekst not in ["Grand Total"]:
                current_product = tekst

        if pd.notna(col5):
            farge = normaliser_variantnavn(col5)

            if farge == "":
                continue

            try:
                lagerverdi = float(stock_value)
            except:
                lagerverdi = 0

            try:
                antall = float(stock_qty)
            except:
                antall = 0

            rader.append({
                "Season": current_season,
                "Brand": current_brand,
                "Group": current_group,
                "Name": current_product,
                "Color": farge,
                "Variant": f"{current_product} {farge}".strip(),
                "Produktnøkkel": lag_variantnokkel(current_product, farge),
                "Lagerkostnad": lagerverdi,
                "Antall_lager": antall,
            })

    df = pd.DataFrame(rader)

    if df.empty:
        return df

    df = df[
        (df["Name"] != "")
        & (df["Color"] != "")
    ]

    return df


def les_front_sales_excel(fil):
    fil.seek(0)
    raw = pd.read_excel(fil, sheet_name=0, header=None)

    rader = []

    current_group = ""
    current_brand = ""
    current_subgroup = ""
    current_product = ""

    for _, row in raw.iterrows():
        col0 = row[0] if 0 in row.index else None
        col1 = row[1] if 1 in row.index else None
        col2 = row[2] if 2 in row.index else None
        col3 = row[3] if 3 in row.index else None

        qty = row[8] if 8 in row.index else row[4] if 4 in row.index else 0
        gross_sales = row[9] if 9 in row.index else row[5] if 5 in row.index else 0
        gross_margin = row[10] if 10 in row.index else row[6] if 6 in row.index else 0
        margin_ratio = row[11] if 11 in row.index else row[7] if 7 in row.index else 0

        if pd.notna(col0):
            tekst = str(col0).strip()
            if tekst.endswith("Total"):
                current_group = tekst.replace(" Total", "").strip()
            elif tekst not in ["Grand Total"]:
                current_group = tekst

        if pd.notna(col1):
            tekst = str(col1).strip()
            if tekst.endswith("Total"):
                current_brand = tekst.replace(" Total", "").strip()
            elif tekst not in ["Grand Total"]:
                current_brand = tekst

        if pd.notna(col2):
            tekst = str(col2).strip()

            if tekst.endswith("Total"):
                current_product = tekst.replace(" Total", "").strip()
            else:
                current_product = tekst

        if pd.notna(col3):
            farge = normaliser_variantnavn(col3)

            if farge == "":
                continue

            try:
                antall_solgt = float(qty)
            except:
                antall_solgt = 0

            try:
                omsetning = float(gross_sales)
            except:
                omsetning = 0

            try:
                bruttofortjeneste = float(gross_margin)
            except:
                bruttofortjeneste = 0

            try:
                margin = float(margin_ratio) * 100
            except:
                margin = 0

            rader.append({
                "Brand": current_brand,
                "Group": current_group,
                "Subgroup": current_subgroup,
                "Produktnavn": current_product,
                "Color": farge,
                "Variant": f"{current_product} {farge}".strip(),
                "Produktnøkkel": lag_variantnokkel(current_product, farge),
                "Antall_solgt": antall_solgt,
                "Omsetning": omsetning,
                "Bruttofortjeneste": bruttofortjeneste,
                "Margin %": margin,
            })

    df = pd.DataFrame(rader)

    if df.empty:
        return df

    df = df[
        (df["Produktnavn"] != "")
        & (df["Color"] != "")
    ]

    return df


def er_front_stock_excel(df, filnavn=""):
    navn = filnavn.lower()
    return "stock" in navn and filnavn.lower().endswith((".xlsx", ".xls"))


def er_front_sales_excel(df, filnavn=""):
    navn = filnavn.lower()
    return "sales" in navn and filnavn.lower().endswith((".xlsx", ".xls"))