# ============================================================
# IKONA FAKTÚRY A FINANCIÍ
# ============================================================

st.markdown(
    f"""
    <div style="
        display:flex;
        justify-content:center;
        align-items:center;
        margin-top:0.2rem;
        margin-bottom:0.7rem;
    ">
        <svg
            width="105"
            height="105"
            viewBox="0 0 120 120"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
            aria-label="Faktúry a financie"
        >

            <!-- Faktúra -->
            <path
                d="M24 16
                   H76
                   C82 16 86 20 86 26
                   V79
                   H70
                   L63 86
                   L56 79
                   L49 86
                   L42 79
                   L35 86
                   L24 79
                   Z"
                stroke="{GREEN}"
                stroke-width="5"
                stroke-linejoin="round"
            />

            <!-- Riadky na faktúre -->
            <line
                x1="35"
                y1="34"
                x2="70"
                y2="34"
                stroke="{GREEN}"
                stroke-width="5"
                stroke-linecap="round"
            />

            <line
                x1="35"
                y1="47"
                x2="61"
                y2="47"
                stroke="{GREEN}"
                stroke-width="5"
                stroke-linecap="round"
            />

            <line
                x1="35"
                y1="60"
                x2="55"
                y2="60"
                stroke="{GREEN}"
                stroke-width="5"
                stroke-linecap="round"
            />

            <!-- Mince -->
            <ellipse
                cx="82"
                cy="69"
                rx="18"
                ry="7"
                stroke="{GREEN}"
                stroke-width="5"
            />

            <path
                d="M64 69
                   V80
                   C64 84 72 88 82 88
                   C92 88 100 84 100 80
                   V69"
                stroke="{GREEN}"
                stroke-width="5"
            />

            <!-- Euro minca -->
            <circle
                cx="91"
                cy="91"
                r="20"
                fill="{BACKGROUND}"
                stroke="{GREEN}"
                stroke-width="5"
            />

            <text
                x="91"
                y="101"
                text-anchor="middle"
                font-size="28"
                font-weight="700"
                fill="{GREEN}"
                font-family="Arial, sans-serif"
            >
                €
            </text>

        </svg>
    </div>
    """,
    unsafe_allow_html=True
)
