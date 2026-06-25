import streamlit as st
import pandas as pd

from modules.helpers import *
from modules.guides import *
from modules.front import *
from modules.zedonk import *
from modules.lager import *
from modules.front_excel import *

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


def finn_rapporttype(df, filnavn=""):
    navn = filnavn.lower()
    cols = set(df.columns)

    if "dagsrapport" in navn:
        return "Front Dagsrapport"

    if navn.endswith((".xlsx", ".xls")) and "stock" in navn:
        return "Front Excel Stock"

    if navn.endswith((".xlsx", ".xls")) and "sales" in navn:
        return "Front Excel Sales"

    if "salg pr varegruppe undergruppe pr butikk" in navn:
        return "Front Salgsrapport"

    if "salg pr kjønn varegruppe pr butikk" in navn:
        return "Front Salgsrapport"

    if {"Customer", "Season"}.issubset(cols) and any("Sub Total (" in c for c in df.columns):
        return "Zedonk Sales Orders"

    if {"StockName", "Season", "Brand", "Group", "Name", "Cost", "Qty"}.issubset(cols):
        return "Lagerverdi"

    if {"Brand", "Group", "ReceiptLabel", "Qty", "Price", "Discount", "Cost"}.issubset(cols):
        return "Front Salgsrapport"

    if {"Brand", "Group", "PRODUCTID_FK", "Qty", "Price", "Discount", "Cost"}.issubset(cols):
        return "Front Salgsrapport"

    return "Ukjent"


st.sidebar.title("Butikkanalyse")
st.sidebar.caption("Data som gir bedre beslutninger")

system = st.sidebar.selectbox(
    "Velg system",
    ["Automatisk", "Front Systems", "Zedonk", "DDD", "Visma", "Shopify", "Annet"]
)

filer = st.sidebar.file_uploader(
    "Last opp rapportfiler",
    type=["csv", "xlsx", "xls"],
    accept_multiple_files=True
)

st.sidebar.divider()

if not filer:
    st.session_state["rapport_kjort"] = False
    vis_startside(system)

else:
    st.sidebar.write("Filer lastet opp:")
    for f in filer:
        st.sidebar.write(f"• {f.name}")

    lager_dfs = []
    salg_dfs = []
    zedonk_dfs = []
    front_excel_stock_dfs = []
    front_excel_sales_dfs = []
    front_dagsrapporter = []
    ukjent_dfs = []
    filinfo = []

    for fil in filer:
        filnavn = fil.name.lower()

        if "dagsrapport" in filnavn:
            front_dagsrapporter.append(fil)
            filinfo.append(f"{fil.name} | Front dagsrapport")
            continue

        try:
            df_fil, enc, sep = les_fil(fil)
            rapporttype = finn_rapporttype(df_fil, fil.name)

            filinfo.append(f"{fil.name} | {rapporttype} | {enc} | sep: {sep}")

            if rapporttype == "Front Excel Stock":
                stock_df = les_front_stock_excel(fil)
                stock_df["Kilde_fil"] = fil.name
                front_excel_stock_dfs.append(stock_df)

            elif rapporttype == "Front Excel Sales":
                sales_df = les_front_sales_excel(fil)
                sales_df["Kilde_fil"] = fil.name
                front_excel_sales_dfs.append(sales_df)

            else:
                df_fil["Kilde_fil"] = fil.name

                if rapporttype == "Lagerverdi":
                    lager_dfs.append(df_fil)
                elif rapporttype == "Front Salgsrapport":
                    salg_dfs.append(df_fil)
                elif rapporttype == "Zedonk Sales Orders":
                    zedonk_dfs.append(df_fil)
                else:
                    ukjent_dfs.append(df_fil)

        except Exception as e:
            filinfo.append(f"{fil.name} | FEIL: {e}")

    with st.expander("Rådata og filinfo"):
        st.write(filinfo)

    if st.button("Lag rapport", type="primary"):
        st.session_state["rapport_kjort"] = True

    if st.session_state.get("rapport_kjort", False):

        if front_excel_stock_dfs and front_excel_sales_dfs:
            st.success("Rapporttype oppdaget: Front Excel Stock + Sales")
            lager_df = pd.concat(front_excel_stock_dfs, ignore_index=True)
            salg_df = pd.concat(front_excel_sales_dfs, ignore_index=True)
            analyser_lager_og_salg(lager_df, salg_df)

        elif front_excel_stock_dfs:
            st.success("Rapporttype oppdaget: Front Excel Stock")
            lager_df = pd.concat(front_excel_stock_dfs, ignore_index=True)
            analyser_lagerverdi(lager_df)

        elif front_excel_sales_dfs:
            st.success("Rapporttype oppdaget: Front Excel Sales")
            salg_df = pd.concat(front_excel_sales_dfs, ignore_index=True)
            analyser_front_salg(salg_df)

        elif lager_dfs and salg_dfs:
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