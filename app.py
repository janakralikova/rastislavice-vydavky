import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Výdavky obce Rastislavice",
    page_icon="📊",
    layout="wide"
)

# -----------------------------
# NAČÍTANIE DÁT
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_excel("Faktury 2026.xlsx")

    df["Dátum zverejnenia"] = pd.to_datetime(
        df["Dátum zverejnenia"],
        dayfirst=True,
        errors="coerce"
    )

    df["Cena (EUR)"] = pd.to_numeric(
        df["Cena (EUR)"],
        errors="coerce"
    )

    df["Mesiac"] = df["Dátum zverejnenia"].dt.month
    df["Mesiac názov"] = df["Dátum zverejnenia"].dt.month_name(locale="C")

    return df


df = load_data()

# -----------------------------
# ŠTÝL
# -----------------------------
st.markdown(
    """
    <style>
    .stApp {
        background-color: #f7f4ef;
    }

    h1, h2, h3 {
        color: #6f4a2f;
    }

    .main-title {
        text-align: center;
        font-size: 2.2rem;
        font-weight: 700;
        color: #6f4a2f;
        margin-bottom: 0.2rem;
    }

    .subtitle {
        text-align: center;
        color: #6b625c;
        margin-bottom: 2rem;
    }

    .info-box {
        background-color: #efe5d8;
        border: 1px solid #d6c2aa;
        padding: 1rem;
        border-radius: 12px;
        margin-top: 1rem;
    }

    .invoice-card {
        background-color: white;
        border: 1px solid #ded6ce;
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 0.7rem;
    }

    .invoice-price {
        font-size: 1.25rem;
        font-weight: 700;
        color: #6f4a2f;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# NADPIS
# -----------------------------
st.markdown(
    '<div class="main-title">Výdavky obce Rastislavice</div>',
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="subtitle">
    Prehľad faktúr zverejnených obcou Rastislavice v roku 2026
    </div>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# HLAVNÉ ČÍSLA
# -----------------------------
total_amount = df["Cena (EUR)"].sum()
invoice_count = len(df)
supplier_count = df["Dodávateľ"].nunique()

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Hodnota zverejnených faktúr",
        f"{total_amount:,.2f} €".replace(",", " ")
    )

with col2:
    st.metric(
        "Počet faktúr",
        f"{invoice_count}"
    )

with col3:
    st.metric(
        "Počet dodávateľov",
        f"{supplier_count}"
    )

st.divider()

# -----------------------------
# VÝDAVKY PODĽA KATEGÓRIÍ
# -----------------------------
st.subheader("Na čo obec nakupovala?")

category_summary = (
    df.groupby("Kategória")["Cena (EUR)"]
    .sum()
    .sort_values(ascending=False)
)

st.bar_chart(category_summary)

with st.expander("Zobraziť prehľad podľa kategórií"):
    category_table = category_summary.reset_index()
    category_table.columns = ["Kategória", "Suma"]
    category_table["Suma"] = category_table["Suma"].map(
        lambda x: f"{x:,.2f} €".replace(",", " ")
    )

    st.dataframe(
        category_table,
        use_container_width=True,
        hide_index=True
    )

st.divider()

# -----------------------------
# DODÁVATELIA
# -----------------------------
st.subheader("Komu obec platila?")

supplier_summary = (
    df.groupby("Dodávateľ")["Cena (EUR)"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

st.bar_chart(supplier_summary)

with st.expander("Zobraziť TOP 10 dodávateľov"):
    supplier_table = supplier_summary.reset_index()
    supplier_table.columns = ["Dodávateľ", "Suma"]
    supplier_table["Suma"] = supplier_table["Suma"].map(
        lambda x: f"{x:,.2f} €".replace(",", " ")
    )

    st.dataframe(
        supplier_table,
        use_container_width=True,
        hide_index=True
    )

st.divider()

# -----------------------------
# FILTRE
# -----------------------------
st.subheader("Vyhľadať vo faktúrach")

filter_col1, filter_col2, filter_col3 = st.columns(3)

with filter_col1:
    categories = ["Všetky"] + sorted(
        df["Kategória"].dropna().unique().tolist()
    )

    selected_category = st.selectbox(
        "Kategória",
        categories
    )

with filter_col2:
    suppliers = ["Všetci"] + sorted(
        df["Dodávateľ"].dropna().unique().tolist()
    )

    selected_supplier = st.selectbox(
        "Dodávateľ",
        suppliers
    )

with filter_col3:
    months = {
        "Všetky mesiace": None,
        "Január": 1,
        "Február": 2,
        "Marec": 3,
        "Apríl": 4,
        "Máj": 5,
        "Jún": 6,
        "Júl": 7,
        "August": 8,
        "September": 9,
        "Október": 10,
        "November": 11,
        "December": 12,
    }

    selected_month_name = st.selectbox(
        "Mesiac",
        list(months.keys())
    )

search_text = st.text_input(
    "Hľadať v popise, čísle faktúry alebo názve dodávateľa",
    placeholder="napr. Brantner, kosačka, energia..."
)

filtered = df.copy()

if selected_category != "Všetky":
    filtered = filtered[
        filtered["Kategória"] == selected_category
    ]

if selected_supplier != "Všetci":
    filtered = filtered[
        filtered["Dodávateľ"] == selected_supplier
    ]

selected_month = months[selected_month_name]

if selected_month is not None:
    filtered = filtered[
        filtered["Mesiac"] == selected_month
    ]

if search_text:
    search_text_lower = search_text.lower()

    filtered = filtered[
        filtered["Popis plnenia"].astype(str).str.lower().str.contains(
            search_text_lower,
            na=False
        )
        |
        filtered["Dodávateľ"].astype(str).str.lower().str.contains(
            search_text_lower,
            na=False
        )
        |
        filtered["Číslo faktúry"].astype(str).str.lower().str.contains(
            search_text_lower,
            na=False
        )
    ]

# -----------------------------
# VÝSLEDOK FILTRA
# -----------------------------
filtered_total = filtered["Cena (EUR)"].sum()

st.markdown(
    f"**Nájdených faktúr:** {len(filtered)}"
)

st.markdown(
    f"**Celková hodnota vybraných faktúr:** "
    f"{filtered_total:,.2f} €".replace(",", " ")
)

st.divider()

# -----------------------------
# ZOZNAM FAKTÚR
# -----------------------------
st.subheader("Prehľad faktúr")

filtered = filtered.sort_values(
    "Dátum zverejnenia",
    ascending=False
)

for _, row in filtered.iterrows():

    date_text = (
        row["Dátum zverejnenia"].strftime("%d.%m.%Y")
        if pd.notna(row["Dátum zverejnenia"])
        else ""
    )

    price_text = (
        f"{row['Cena (EUR)']:,.2f} €".replace(",", " ")
        if pd.notna(row["Cena (EUR)"])
        else ""
    )

    title = (
        f"{row['Dodávateľ']} — "
        f"{price_text}"
    )

    with st.expander(title):

        st.markdown(
            f"### {row['Popis plnenia']}"
        )

        st.write(
            f"**Cena:** {price_text}"
        )

        st.write(
            f"**Dodávateľ:** {row['Dodávateľ']}"
        )

        st.write(
            f"**Dátum zverejnenia:** {date_text}"
        )

        st.write(
            f"**Číslo faktúry:** {row['Číslo faktúry']}"
        )

        st.write(
            f"**Kategória:** {row['Kategória']}"
        )

# -----------------------------
# POZNÁMKY
# -----------------------------
st.divider()

st.markdown(
    """
    <div class="info-box">

    <b>Zdroj údajov:</b> faktúry zverejnené obcou Rastislavice.

    <br><br>

    Prehľad slúži na jednoduchšie vyhľadávanie a orientáciu
    vo verejne dostupných údajoch.

    <br><br>

    <b>Poznámka:</b> Faktúry s číslom začínajúcim na rok 2025
    boli zverejnené v roku 2026.

    <br><br>

    Kategórie boli vytvorené pre jednoduchšiu orientáciu občanov
    a nepredstavujú ekonomickú klasifikáciu rozpočtu.

    </div>
    """,
    unsafe_allow_html=True
)
