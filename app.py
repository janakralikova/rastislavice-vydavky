import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import math


# ============================================================
# NASTAVENIE STRÁNKY
# ============================================================

st.set_page_config(
    page_title="Výdavky obce Rastislavice",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ============================================================
# FARBY
# ============================================================

BACKGROUND = "#e5d6c2"
BROWN = "#7b3f06"
BROWN_MEDIUM = "#9b6535"
BROWN_LIGHT = "#c49a6c"
CREAM = "#fffaf4"
CREAM_DARK = "#f3e8da"
BORDER = "#ccb18f"
TEXT = "#4c3425"
MUTED = "#75675d"


# ============================================================
# POMOCNÉ FUNKCIE
# ============================================================

def format_eur(value):
    """Slovenský formát meny: 12 345,67 €"""
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

    missing = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            "V Exceli chýbajú stĺpce: "
            + ", ".join(missing)
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

    df["Mesiac"] = df["Dátum zverejnenia"].dt.month

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
# CSS – VIZUÁL APLIKÁCIE
# ============================================================

st.markdown(
    f"""
    <style>

    /* --------------------------------------------------------
       CELÁ APLIKÁCIA
       -------------------------------------------------------- */

    .stApp {{
        background:
            radial-gradient(
                circle at top,
                #efe4d5 0%,
                {BACKGROUND} 45%,
                #ddccb7 100%
            );
        color: {TEXT};
    }}

    .block-container {{
        max-width: 1180px;
        padding-top: 1.4rem;
        padding-bottom: 4rem;
    }}


    /* --------------------------------------------------------
       NADPISY
       -------------------------------------------------------- */

    h1, h2, h3 {{
        color: {BROWN} !important;
        font-family:
            -apple-system,
            BlinkMacSystemFont,
            "Segoe UI",
            sans-serif;
    }}

    .main-title {{
        text-align: center;
        color: {BROWN};
        font-weight: 800;
        font-size: clamp(2rem, 5vw, 3rem);
        line-height: 1.08;
        letter-spacing: -0.035em;
        margin-top: 0.25rem;
        margin-bottom: 0.45rem;
    }}

    .main-subtitle {{
        max-width: 760px;
        margin: 0 auto 1.8rem auto;
        text-align: center;
        color: {MUTED};
        font-size: 1.02rem;
        line-height: 1.6;
    }}

    .section-title {{
        color: {BROWN};
        font-size: 1.55rem;
        font-weight: 800;
        margin-top: 1rem;
        margin-bottom: 0.15rem;
    }}

    .section-description {{
        color: {MUTED};
        font-size: 0.95rem;
        margin-bottom: 1rem;
    }}


    /* --------------------------------------------------------
       METRIKY
       -------------------------------------------------------- */

    [data-testid="stMetric"] {{
        background:
            linear-gradient(
                145deg,
                #fffdf9,
                {CREAM_DARK}
            );
        border: 1px solid {BORDER};
        border-radius: 18px;
        padding: 1.05rem 1.15rem;
        box-shadow:
            0 8px 20px rgba(90, 54, 24, 0.08),
            inset 0 1px 0 rgba(255,255,255,0.9);
        min-height: 120px;
    }}

    [data-testid="stMetricLabel"] {{
        color: {MUTED};
        font-weight: 600;
    }}

    [data-testid="stMetricValue"] {{
        color: {BROWN};
        font-weight: 800;
    }}


    /* --------------------------------------------------------
       VSTUPNÉ POLIA
       -------------------------------------------------------- */

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


    /* --------------------------------------------------------
       EXPANDERY / FAKTÚRY
       -------------------------------------------------------- */

    [data-testid="stExpander"] {{
        background: rgba(255, 250, 244, 0.92);
        border: 1px solid {BORDER};
        border-radius: 14px;
        margin-bottom: 0.55rem;
        box-shadow:
            0 3px 10px rgba(90, 54, 24, 0.045);
        overflow: hidden;
    }}

    [data-testid="stExpander"] summary {{
        font-weight: 600;
        color: {TEXT};
    }}


    /* --------------------------------------------------------
       INFO BOX
       -------------------------------------------------------- */

    .info-box {{
        background:
            linear-gradient(
                145deg,
                {CREAM_DARK},
                #ead9c5
            );
        border: 1px solid {BORDER};
        border-left: 5px solid {BROWN};
        padding: 1.2rem 1.35rem;
        border-radius: 14px;
        color: {TEXT};
        line-height: 1.6;
        margin-top: 1.2rem;
        box-shadow:
            0 5px 14px rgba(90, 54, 24, 0.06);
    }}


    /* --------------------------------------------------------
       VÝSLEDKY FILTRA
       -------------------------------------------------------- */

    .filter-summary {{
        background: {CREAM};
        border: 1px solid {BORDER};
        border-radius: 15px;
        padding: 0.9rem 1.1rem;
        margin: 1rem 0 1.15rem 0;
        color: {TEXT};
        box-shadow:
            0 4px 12px rgba(90, 54, 24, 0.05);
    }}

    .filter-number {{
        color: {BROWN};
        font-weight: 800;
    }}


    /* --------------------------------------------------------
       MALÝ ŠTÍTOK KATEGÓRIE
       -------------------------------------------------------- */

    .category-badge {{
        display: inline-block;
        background-color: {CREAM_DARK};
        color: {BROWN};
        border: 1px solid {BORDER};
        border-radius: 999px;
        padding: 0.26rem 0.7rem;
        font-size: 0.82rem;
        font-weight: 700;
        margin-top: 0.25rem;
    }}


    /* --------------------------------------------------------
       ODDEĽOVAČ
       -------------------------------------------------------- */

    hr {{
        border-color: rgba(123, 63, 6, 0.15);
    }}


    /* --------------------------------------------------------
       MOBIL
       -------------------------------------------------------- */

    @media (max-width: 700px) {{

        .block-container {{
            padding-left: 1rem;
            padding-right: 1rem;
            padding-top: 0.8rem;
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
# LOGO
# rovnaké riešenie ako pri aplikácii Rastislavice zdieľajú
# ============================================================

logo_left, logo_center, logo_right = st.columns(
    [1, 1.25, 1]
)

with logo_center:
    try:
        st.image(
            "logo.png",
            use_container_width=True
        )
    except Exception:
        pass


# ============================================================
# HLAVIČKA
# ============================================================

st.markdown(
    """
    <div class="main-title">
        Výdavky obce Rastislavice
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="main-subtitle">
        Jednoduchý a prehľadný pohľad na faktúry
        zverejnené obcou Rastislavice v roku 2026.
        Pozrite sa, za čo obec platí a komu smerujú
        verejné prostriedky.
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# ZÁKLADNÉ ČÍSLA
# ============================================================

total_amount = df["Cena (EUR)"].sum()
invoice_count = len(df)
supplier_count = df["Dodávateľ"].nunique()

metric1, metric2, metric3 = st.columns(3)

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


st.markdown("<br>", unsafe_allow_html=True)


# ============================================================
# FUNKCIA PRE 3D GRAF
# ============================================================

def create_3d_bar_chart(
    data,
    title,
    max_items=None,
    height=560
):

    if max_items:
        data = data.head(max_items)

    data = data.sort_values(
        ascending=False
    )

    labels = list(data.index)
    values = list(data.values)

    if not values:
        return go.Figure()

    # Hnedé odtiene.
    brown_palette = [
        "#6b3505",
        "#75400d",
        "#7f4a16",
        "#89541f",
        "#935e28",
        "#9d6831",
        "#a7723b",
        "#b17c45",
        "#bb8750",
        "#c4915b",
        "#cc9b66",
        "#d3a572",
    ]

    fig = go.Figure()

    depth = 0.58
    width = 0.64

    max_value = max(values)

    for i, (label, value) in enumerate(
        zip(labels, values)
    ):

        x0 = i - width / 2
        x1 = i + width / 2

        y0 = 0
        y1 = depth

        z0 = 0
        z1 = float(value)

        x = [
            x0, x1, x1, x0,
            x0, x1, x1, x0
        ]

        y = [
            y0, y0, y1, y1,
            y0, y0, y1, y1
        ]

        z = [
            z0, z0, z0, z0,
            z1, z1, z1, z1
        ]

        # Trojuholníky tvoriace kváder
        I = [
            0, 0,
            4, 4,
            0, 0,
            1, 1,
            2, 2,
            3, 3
        ]

        J = [
            1, 2,
            5, 6,
            1, 5,
            2, 6,
            3, 7,
            0, 4
        ]

        K = [
            2, 3,
            6, 7,
            5, 4,
            6, 5,
            7, 6,
            4, 7
        ]

        color = brown_palette[
            min(
                i,
                len(brown_palette) - 1
            )
        ]

        fig.add_trace(
            go.Mesh3d(
                x=x,
                y=y,
                z=z,
                i=I,
                j=J,
                k=K,
                color=color,
                opacity=0.96,
                flatshading=True,
                hovertemplate=(
                    f"<b>{label}</b><br>"
                    f"{format_eur(value)}"
                    "<extra></extra>"
                ),
                name=str(label),
                showscale=False,
                showlegend=False
            )
        )

        # Hodnota nad stĺpcom
        fig.add_trace(
            go.Scatter3d(
                x=[i],
                y=[depth / 2],
                z=[
                    float(value)
                    + max_value * 0.035
                ],
                mode="text",
                text=[
                    format_eur(value)
                ],
                textfont=dict(
                    size=11,
                    color=BROWN
                ),
                hoverinfo="skip",
                showlegend=False
            )
        )

    fig.update_layout(

        height=height,

        margin=dict(
            l=0,
            r=0,
            b=0,
            t=40
        ),

        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",

        scene=dict(

            bgcolor="rgba(0,0,0,0)",

            camera=dict(
                eye=dict(
                    x=1.5,
                    y=-1.8,
                    z=1.05
                )
            ),

            xaxis=dict(
                tickmode="array",
                tickvals=list(
                    range(len(labels))
                ),
                ticktext=labels,
                tickfont=dict(
                    size=10,
                    color=TEXT
                ),
                title="",
                showgrid=False,
                zeroline=False,
                backgroundcolor="rgba(0,0,0,0)"
            ),

            yaxis=dict(
                visible=False,
                showgrid=False,
                zeroline=False
            ),

            zaxis=dict(
                title="EUR",
                titlefont=dict(
                    color=MUTED
                ),
                tickfont=dict(
                    color=MUTED
                ),
                gridcolor="rgba(123,63,6,0.10)",
                zerolinecolor="rgba(123,63,6,0.25)",
                backgroundcolor="rgba(255,250,244,0.15)"
            ),

            aspectmode="manual",

            aspectratio=dict(
                x=max(
                    1.8,
                    len(labels) * 0.34
                ),
                y=0.7,
                z=1.55
            )
        ),

        font=dict(
            family="Arial",
            color=TEXT
        )
    )

    return fig


# ============================================================
# KATEGÓRIE
# ============================================================

st.markdown(
    """
    <div class="section-title">
        Na čo obec míňa prostriedky?
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="section-description">
        Prehľad zverejnených faktúr podľa kategórií.
        Výška stĺpca predstavuje celkovú hodnotu faktúr
        zaradených do danej kategórie.
    </div>
    """,
    unsafe_allow_html=True
)

category_summary = (
    df.groupby("Kategória")["Cena (EUR)"]
    .sum()
    .sort_values(ascending=False)
)

# Aby bol 3D graf čitateľný,
# ukážeme prvých 10 kategórií.
category_chart = create_3d_bar_chart(
    category_summary,
    "Výdavky podľa kategórií",
    max_items=10,
    height=570
)

st.plotly_chart(
    category_chart,
    use_container_width=True,
    config={
        "displayModeBar": False
    }
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
    ] = category_table[
        "Hodnota faktúr"
    ].apply(format_eur)

    st.dataframe(
        category_table,
        use_container_width=True,
        hide_index=True
    )


st.divider()


# ============================================================
# DODÁVATELIA
# ============================================================

st.markdown(
    """
    <div class="section-title">
        Komu obec platila?
    </div>
    """,
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
    df.groupby("Dodávateľ")["Cena (EUR)"]
    .sum()
    .sort_values(ascending=False)
)

supplier_chart = create_3d_bar_chart(
    supplier_summary,
    "Najväčší dodávatelia",
    max_items=10,
    height=570
)

st.plotly_chart(
    supplier_chart,
    use_container_width=True,
    config={
        "displayModeBar": False
    }
)


with st.expander(
    "Zobraziť TOP 10 dodávateľov",
    icon=":material/business:"
):

    supplier_table = (
        supplier_summary
        .head(10)
        .reset_index()
    )

    supplier_table.columns = [
        "Dodávateľ",
        "Hodnota faktúr"
    ]

    supplier_table[
        "Hodnota faktúr"
    ] = supplier_table[
        "Hodnota faktúr"
    ].apply(format_eur)

    st.dataframe(
        supplier_table,
        use_container_width=True,
        hide_index=True
    )


st.divider()


# ============================================================
# VYHĽADÁVANIE
# ============================================================

st.markdown(
    """
    <div class="section-title">
        Nájdite konkrétnu faktúru
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="section-description">
        Vyberte kategóriu, dodávateľa alebo mesiac.
        Môžete tiež vyhľadávať podľa ľubovoľného slova.
    </div>
    """,
    unsafe_allow_html=True
)


filter_col1, filter_col2, filter_col3 = st.columns(3)


with filter_col1:

    categories = (
        ["Všetky kategórie"]
        + sorted(
            df["Kategória"]
            .dropna()
            .unique()
            .tolist()
        )
    )

    selected_category = st.selectbox(
        "Kategória",
        categories
    )


with filter_col2:

    suppliers = (
        ["Všetci dodávatelia"]
        + sorted(
            df["Dodávateľ"]
            .dropna()
            .unique()
            .tolist()
        )
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
    "Vyhľadávanie",
    placeholder=(
        "Napr. Brantner, kosačka, energia, "
        "číslo faktúry..."
    ),
    icon=":material/search:"
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


selected_month = months[
    selected_month_name
]

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

    filtered = filtered[
        search_mask
    ]


# ============================================================
# SÚHRN FILTRA
# ============================================================

filtered_total = filtered[
    "Cena (EUR)"
].sum()


st.markdown(
    f"""
    <div class="filter-summary">

        <span class="filter-number">
            {format_number(len(filtered))}
        </span>
        faktúr

        &nbsp;&nbsp;•&nbsp;&nbsp;

        hodnota vybraných faktúr:

        <span class="filter-number">
            {format_eur(filtered_total)}
        </span>

    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# ZOZNAM FAKTÚR
# ============================================================

st.markdown(
    """
    <div class="section-title">
        Prehľad faktúr
    </div>
    """,
    unsafe_allow_html=True
)


if filtered.empty:

    st.info(
        "Pre zvolené podmienky sa nenašla žiadna faktúra."
    )

else:

    filtered = filtered.sort_values(
        "Dátum zverejnenia",
        ascending=False
    )

    for _, row in filtered.iterrows():

        if pd.notna(
            row["Dátum zverejnenia"]
        ):

            date_text = (
                row["Dátum zverejnenia"]
                .strftime("%d.%m.%Y")
            )

        else:
            date_text = "—"


        price_text = format_eur(
            row["Cena (EUR)"]
        )


        expander_title = (
            f"{row['Dodávateľ']}  ·  "
            f"{price_text}"
        )


        with st.expander(
            expander_title,
            icon=":material/receipt_long:"
        ):

            st.markdown(
                f"""
                <div style="
                    font-size:1.15rem;
                    font-weight:750;
                    color:{BROWN};
                    margin-bottom:0.8rem;
                ">
                    {row["Popis plnenia"]}
                </div>
                """,
                unsafe_allow_html=True
            )


            detail_col1, detail_col2 = (
                st.columns([1, 1])
            )


            with detail_col1:

                st.markdown(
                    f"**Cena:** {price_text}"
                )

                st.markdown(
                    f"**Dodávateľ:** "
                    f"{row['Dodávateľ']}"
                )

                st.markdown(
                    f"**Kategória:** "
                    f"{row['Kategória']}"
                )


            with detail_col2:

                st.markdown(
                    f"**Dátum zverejnenia:** "
                    f"{date_text}"
                )

                st.markdown(
                    f"**Číslo faktúry:** "
                    f"{row['Číslo faktúry']}"
                )


            st.markdown(
                f"""
                <span class="category-badge">
                    {row["Kategória"]}
                </span>
                """,
                unsafe_allow_html=True
            )


# ============================================================
# ZDROJ A VYSVETLENIE
# ============================================================

st.divider()


with st.expander(
    "O údajoch v aplikácii",
    icon=":material/info:"
):

    st.markdown(
        """
        **Zdroj údajov:** faktúry zverejnené
        obcou Rastislavice.

        Aplikácia slúži na jednoduchšie vyhľadávanie
        a zobrazenie verejne dostupných údajov.

        **Hodnota zverejnených faktúr nepredstavuje
        automaticky aktuálne čerpanie rozpočtu obce.**

        Kategórie boli vytvorené pre jednoduchšiu
        orientáciu občanov a nepredstavujú ekonomickú
        klasifikáciu rozpočtu.

        **Poznámka:** Faktúry s číslom začínajúcim
        na rok 2025 boli zverejnené v roku 2026.
        """
    )


# ============================================================
# PÄTIČKA
# ============================================================

st.markdown(
    f"""
    <div style="
        text-align:center;
        color:{MUTED};
        font-size:0.82rem;
        margin-top:2.5rem;
        padding-top:1rem;
        border-top:1px solid rgba(123,63,6,0.12);
    ">
        Prehľad verejne dostupných údajov
        • Rastislavice 2026
    </div>
    """,
    unsafe_allow_html=True
)
