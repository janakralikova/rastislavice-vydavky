import streamlit as st
import pandas as pd
import html


# ============================================================
# NASTAVENIE STRÁNKY
# ============================================================

st.set_page_config(
    page_title="Výdavky obce Rastislavice",
    page_icon="€",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ============================================================
# FARBY
# ============================================================

BACKGROUND = "#E4EBDD"
GREEN = "#2F5D50"
CREAM = "#F7FAF4"
CREAM_DARK = "#EDF3E9"
BORDER = "#B8C9B4"
TEXT = "#2E4038"
MUTED = "#65746C"


# ============================================================
# POMOCNÉ FUNKCIE
# ============================================================

def format_eur(value):

    if pd.isna(value):
        return "—"

    formatted = f"{float(value):,.2f}"

    formatted = (
        formatted
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", " ")
    )

    return f"{formatted} €"


def format_number(value):

    if pd.isna(value):
        return "—"

    return f"{int(value):,}".replace(",", " ")


def clean_invoice_number(value):

    if pd.isna(value):
        return ""

    try:
        return str(int(float(value)))

    except Exception:
        return str(value)


# ============================================================
# NAČÍTANIE DÁT
# ============================================================

@st.cache_data
def load_data():

    df = pd.read_excel("Faktury 2026.xlsx")

    required_columns = [
        "Dátum zverejnenia",
        "Číslo faktúry",
        "Popis plnenia",
        "Cena (EUR)",
        "Dodávateľ",
        "Kategória",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:

        raise ValueError(
            "V Exceli chýbajú stĺpce: "
            + ", ".join(missing_columns)
        )

    df["Dátum zverejnenia"] = pd.to_datetime(
        df["Dátum zverejnenia"],
        dayfirst=True,
        errors="coerce"
    )

    df["Cena (EUR)"] = pd.to_numeric(
        df["Cena (EUR)"],
        errors="coerce"
    )

    df["Číslo faktúry"] = (
        df["Číslo faktúry"]
        .apply(clean_invoice_number)
    )

    df["Kategória"] = (
        df["Kategória"]
        .fillna("Bez kategórie")
        .astype(str)
        .str.strip()
    )

    df["Dodávateľ"] = (
        df["Dodávateľ"]
        .fillna("Neuvedený dodávateľ")
        .astype(str)
        .str.strip()
    )

    df["Popis plnenia"] = (
        df["Popis plnenia"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    df["Mesiac"] = (
        df["Dátum zverejnenia"]
        .dt.month
    )

    return df


try:

    df = load_data()

except Exception as error:

    st.error(
        "Nepodarilo sa načítať súbor Faktury 2026.xlsx."
    )

    st.exception(error)

    st.stop()


# ============================================================
# VZHĽAD
# ============================================================

st.markdown(
    f"""
    <style>

    .stApp {{
        background:
            linear-gradient(
                180deg,
                #EDF3E9 0%,
                {BACKGROUND} 38%,
                {BACKGROUND} 100%
            );
        color: {TEXT};
    }}

    .block-container {{
        max-width: 1160px;
        padding-top: 3.5rem;
        padding-bottom: 4rem;
    }}

    h1, h2, h3 {{
        color: {GREEN} !important;
    }}

    .finance-icon {{
        width: 88px;
        height: 88px;
        border: 4px solid {GREEN};
        border-radius: 50%;
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 0.2rem auto 0.7rem auto;
        color: {GREEN};
        font-size: 3.3rem;
        font-weight: 800;
        line-height: 1;
        font-family: Arial, sans-serif;
        box-sizing: border-box;
    }}

    .main-title {{
        text-align: center;
        color: {GREEN};
        font-weight: 800;
        font-size: clamp(2rem, 5vw, 3rem);
        line-height: 1.1;
        letter-spacing: -0.035em;
        margin-top: 0.2rem;
        margin-bottom: 0.4rem;
    }}

    .main-subtitle {{
        max-width: 720px;
        margin: 0 auto 1.2rem auto;
        text-align: center;
        color: {MUTED};
        font-size: 1rem;
        line-height: 1.6;
    }}

    .section-title {{
        color: {GREEN};
        font-size: 1.55rem;
        font-weight: 800;
        margin-top: 1rem;
        margin-bottom: 0.2rem;
    }}

    .section-description {{
        color: {MUTED};
        font-size: 0.95rem;
        line-height: 1.5;
        margin-bottom: 1rem;
    }}

    [data-testid="stMetric"] {{
        background:
            linear-gradient(
                145deg,
                #FBFDF9,
                {CREAM_DARK}
            );
        border: 1px solid {BORDER};
        border-radius: 18px;
        padding: 1rem 1.15rem;
        min-height: 115px;
        box-shadow:
            0 8px 22px rgba(47, 93, 80, 0.08),
            inset 0 1px 0 rgba(255,255,255,0.9);
    }}

    [data-testid="stMetricLabel"] {{
        color: {MUTED};
        font-weight: 600;
    }}

    [data-testid="stMetricValue"] {{
        color: {GREEN};
        font-weight: 800;
    }}

    div[data-baseweb="select"] > div {{
        background-color: {CREAM} !important;
        border-color: {BORDER} !important;
        border-radius: 12px !important;
    }}

    div[data-baseweb="input"] > div {{
        background-color: {CREAM} !important;
        border-color: {BORDER} !important;
        border-radius: 12px !important;
    }}

    input {{
        color: {TEXT} !important;
    }}

    [data-testid="stExpander"] {{
        background-color: rgba(247,250,244,0.96);
        border: 1px solid {BORDER};
        border-radius: 14px;
        margin-bottom: 0.55rem;
        box-shadow:
            0 3px 10px rgba(47,93,80,0.05);
    }}

    [data-testid="stExpander"] summary {{
        color: {TEXT};
        font-weight: 600;
    }}

    .category-badge {{
        display: inline-block;
        background-color: {CREAM_DARK};
        color: {GREEN};
        border: 1px solid {BORDER};
        border-radius: 999px;
        padding: 0.27rem 0.7rem;
        margin-top: 0.4rem;
        font-size: 0.82rem;
        font-weight: 700;
    }}

    .footer {{
        text-align: center;
        color: {MUTED};
        font-size: 0.82rem;
        margin-top: 2.5rem;
        padding-top: 1rem;
        border-top:
            1px solid
            rgba(47,93,80,0.16);
    }}

    hr {{
        border-color:
            rgba(47,93,80,0.15);
    }}

    @media (max-width: 700px) {{

        .block-container {{
            padding-left: 1rem;
            padding-right: 1rem;
            padding-top: 2.5rem;
        }}

        .finance-icon {{
            width: 72px;
            height: 72px;
            font-size: 2.7rem;
            border-width: 3px;
        }}

        .main-title {{
            font-size: 2rem;
        }}

        .main-subtitle {{
            font-size: 0.92rem;
        }}

        .section-title {{
            font-size: 1.35rem;
        }}

    }}

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# IKONA FINANCIÍ
# ============================================================

st.markdown(
    '<div class="finance-icon">€</div>',
    unsafe_allow_html=True
)


# ============================================================
# HLAVIČKA
# ============================================================

st.markdown(
    '<div class="main-title">Výdavky obce Rastislavice</div>',
    unsafe_allow_html=True
)


st.markdown(
    """
    <div class="main-subtitle">
        Prehľad faktúr zverejnených obcou Rastislavice
        v roku 2026.<br>
        Jednoducho si môžete pozrieť,
        <b>za čo obec platí a kam smerujú verejné prostriedky.</b>
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# INFORMÁCIE O ÚDAJOCH
# ============================================================

with st.expander(
    "O údajoch v aplikácii",
    icon=":material/info:"
):

    st.markdown(
        """
        **Zdroj údajov:** faktúry zverejnené obcou Rastislavice.

        Aplikácia slúži na jednoduchšie vyhľadávanie
        a zobrazenie verejne dostupných údajov.

        **Hodnota zverejnených faktúr nepredstavuje
        automaticky aktuálne čerpanie rozpočtu obce.**

        **Kategórie boli doplnené pre jednoduchšiu orientáciu občanov.
        Nejde o oficiálnu ekonomickú klasifikáciu obce.
        Zaradenie jednotlivých faktúr bolo vytvorené manuálne
        a napriek snahe o čo najväčšiu presnosť sa môže vyskytnúť chyba.**

        **Poznámka:** Faktúry s číslom začínajúcim
        na rok 2025 boli zverejnené v roku 2026.
        """
    )


st.markdown(
    "<br>",
    unsafe_allow_html=True
)


# ============================================================
# HLAVNÉ ČÍSLA
# ============================================================

total_amount = (
    df["Cena (EUR)"]
    .sum()
)

invoice_count = len(df)

supplier_count = (
    df["Dodávateľ"]
    .nunique()
)


metric1, metric2, metric3 = (
    st.columns(3)
)


with metric1:

    st.metric(
        "Hodnota zverejnených faktúr",
        format_eur(total_amount)
    )


with metric2:

    st.metric(
        "Počet faktúr",
        format_number(invoice_count)
    )


with metric3:

    st.metric(
        "Počet dodávateľov",
        format_number(supplier_count)
    )


st.markdown(
    "<br>",
    unsafe_allow_html=True
)


# ============================================================
# KATEGÓRIE
# ============================================================

st.markdown(
    '<div class="section-title">Na čo obec míňa prostriedky?</div>',
    unsafe_allow_html=True
)


st.markdown(
    """
    <div class="section-description">
        Súhrnná hodnota zverejnených faktúr
        podľa jednotlivých kategórií.
    </div>
    """,
    unsafe_allow_html=True
)


category_summary = (
    df
    .groupby("Kategória")["Cena (EUR)"]
    .sum()
    .sort_values(
        ascending=False
    )
)


st.bar_chart(
    category_summary,
    color=GREEN,
    height=430
)


with st.expander(
    "Zobraziť všetky kategórie",
    icon=":material/category:"
):

    category_table = (
        category_summary
        .reset_index()
    )

    category_table.columns = [
        "Kategória",
        "Hodnota faktúr"
    ]

    category_table[
        "Hodnota faktúr"
    ] = (
        category_table[
            "Hodnota faktúr"
        ]
        .apply(format_eur)
    )

    st.dataframe(
        category_table,
        width="stretch",
        hide_index=True
    )


st.divider()


# ============================================================
# DODÁVATELIA
# ============================================================

st.markdown(
    '<div class="section-title">Komu obec platila?</div>',
    unsafe_allow_html=True
)


st.markdown(
    """
    <div class="section-description">
        Desať dodávateľov s najvyššou celkovou hodnotou
        zverejnených faktúr.
    </div>
    """,
    unsafe_allow_html=True
)


supplier_summary = (
    df
    .groupby("Dodávateľ")["Cena (EUR)"]
    .sum()
    .sort_values(
        ascending=False
    )
)


top_suppliers = (
    supplier_summary
    .head(10)
)


st.bar_chart(
    top_suppliers,
    color=GREEN,
    height=430
)


with st.expander(
    "Zobraziť TOP 10 dodávateľov",
    icon=":material/business:"
):

    supplier_table = (
        top_suppliers
        .reset_index()
    )

    supplier_table.columns = [
        "Dodávateľ",
        "Hodnota faktúr"
    ]

    supplier_table[
        "Hodnota faktúr"
    ] = (
        supplier_table[
            "Hodnota faktúr"
        ]
        .apply(format_eur)
    )

    st.dataframe(
        supplier_table,
        width="stretch",
        hide_index=True
    )


st.divider()


# ============================================================
# VYHĽADÁVANIE
# ============================================================

st.markdown(
    '<div class="section-title">Nájdite konkrétnu faktúru</div>',
    unsafe_allow_html=True
)


st.markdown(
    """
    <div class="section-description">
        Prehľad môžete filtrovať podľa kategórie,
        dodávateľa alebo mesiaca.
        Vyhľadávať môžete aj podľa ľubovoľného slova.
    </div>
    """,
    unsafe_allow_html=True
)


filter_col1, filter_col2, filter_col3 = (
    st.columns(3)
)


with filter_col1:

    categories = (
        ["Všetky kategórie"]
        +
        sorted(
            df["Kategória"]
            .dropna()
            .unique()
            .tolist()
        )
    )

    selected_category = (
        st.selectbox(
            "Kategória",
            categories
        )
    )


with filter_col2:

    suppliers = (
        ["Všetci dodávatelia"]
        +
        sorted(
            df["Dodávateľ"]
            .dropna()
            .unique()
            .tolist()
        )
    )

    selected_supplier = (
        st.selectbox(
            "Dodávateľ",
            suppliers
        )
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
        "December": 12
    }

    selected_month_name = (
        st.selectbox(
            "Mesiac",
            list(
                months.keys()
            )
        )
    )


search_text = (
    st.text_input(
        "Vyhľadávanie",
        placeholder=(
            "Napr. Brantner, kosačka, energia, číslo faktúry..."
        ),
        icon=":material/search:"
    )
)


# ============================================================
# FILTROVANIE
# ============================================================

filtered = df.copy()


if selected_category != "Všetky kategórie":

    filtered = filtered[
        filtered["Kategória"]
        == selected_category
    ]


if selected_supplier != "Všetci dodávatelia":

    filtered = filtered[
        filtered["Dodávateľ"]
        == selected_supplier
    ]


selected_month = (
    months[
        selected_month_name
    ]
)


if selected_month is not None:

    filtered = filtered[
        filtered["Mesiac"]
        == selected_month
    ]


if search_text:

    search_lower = (
        search_text
        .strip()
        .lower()
    )


    search_mask = (

        filtered[
            "Popis plnenia"
        ]
        .astype(str)
        .str.lower()
        .str.contains(
            search_lower,
            regex=False,
            na=False
        )

        |

        filtered[
            "Dodávateľ"
        ]
        .astype(str)
        .str.lower()
        .str.contains(
            search_lower,
            regex=False,
            na=False
        )

        |

        filtered[
            "Číslo faktúry"
        ]
        .astype(str)
        .str.lower()
        .str.contains(
            search_lower,
            regex=False,
            na=False
        )

        |

        filtered[
            "Kategória"
        ]
        .astype(str)
        .str.lower()
        .str.contains(
            search_lower,
            regex=False,
            na=False
        )
    )


    filtered = (
        filtered[
            search_mask
        ]
    )


# ============================================================
# SÚHRN VYHĽADÁVANIA
# ============================================================

filtered_total = (
    filtered[
        "Cena (EUR)"
    ]
    .sum()
)


result_col1, result_col2 = (
    st.columns(2)
)


with result_col1:

    st.metric(
        "Nájdených faktúr",
        format_number(
            len(filtered)
        )
    )


with result_col2:

    st.metric(
        "Hodnota vybraných faktúr",
        format_eur(
            filtered_total
        )
    )


st.markdown(
    "<br>",
    unsafe_allow_html=True
)


# ============================================================
# PREHĽAD FAKTÚR
# ============================================================

st.markdown(
    '<div class="section-title">Prehľad faktúr</div>',
    unsafe_allow_html=True
)


if filtered.empty:

    st.info(
        "Pre zvolené podmienky sa nenašla žiadna faktúra."
    )


else:

    filtered = (
        filtered
        .sort_values(
            "Dátum zverejnenia",
            ascending=False
        )
    )


    for _, row in filtered.iterrows():

        if pd.notna(
            row["Dátum zverejnenia"]
        ):

            date_text = (
                row[
                    "Dátum zverejnenia"
                ]
                .strftime(
                    "%d.%m.%Y"
                )
            )

        else:

            date_text = "—"


        price_text = (
            format_eur(
                row[
                    "Cena (EUR)"
                ]
            )
        )


        supplier_text = html.escape(
            str(
                row[
                    "Dodávateľ"
                ]
            )
        )


        description_text = html.escape(
            str(
                row[
                    "Popis plnenia"
                ]
            )
        )


        category_text = html.escape(
            str(
                row[
                    "Kategória"
                ]
            )
        )


        invoice_number = html.escape(
            str(
                row[
                    "Číslo faktúry"
                ]
            )
        )


        expander_title = (
            f"{row['Dodávateľ']} · "
            f"{price_text}"
        )


        with st.expander(
            expander_title,
            icon=":material/receipt_long:"
        ):

            st.markdown(
                f"""
                <div style="
                    font-size:1.12rem;
                    font-weight:750;
                    color:{GREEN};
                    margin-bottom:0.9rem;
                ">
                    {description_text}
                </div>
                """,
                unsafe_allow_html=True
            )


            detail_col1, detail_col2 = (
                st.columns(2)
            )


            with detail_col1:

                st.markdown(
                    f"**Cena:** "
                    f"{price_text}"
                )

                st.markdown(
                    f"**Dodávateľ:** "
                    f"{supplier_text}"
                )

                st.markdown(
                    f"**Kategória:** "
                    f"{category_text}"
                )


            with detail_col2:

                st.markdown(
                    f"**Dátum zverejnenia:** "
                    f"{date_text}"
                )

                st.markdown(
                    f"**Číslo faktúry:** "
                    f"{invoice_number}"
                )


            st.markdown(
                f"""
                <span class="category-badge">
                    {category_text}
                </span>
                """,
                unsafe_allow_html=True
            )


# ============================================================
# PÄTIČKA
# ============================================================

st.markdown(
    """
    <div class="footer">
        Prehľad verejne dostupných údajov • Rastislavice 2026
    </div>
    """,
    unsafe_allow_html=True
)
