import streamlit


def bot_selection_style(st: streamlit.session_state) -> str:
    # ── Sidebar: branding only ──────────────────────────────
    with st.sidebar:
        st.markdown("""
            <div style="text-align:center; padding: 1.5rem 0 1rem;">
                <div style="font-size:3rem; line-height:1;">🐾</div>
                <div style="font-size:1.25rem; font-weight:800; color:#f1f5f9;
                            letter-spacing:-0.02em; margin-top:0.6rem;">Catbot</div>
                <div style="font-size:0.75rem; color:#334155;
                            text-transform:uppercase; letter-spacing:0.1em;
                            margin-top:0.2rem;">AI Chat Suite</div>
            </div>
            <hr style="border:none; border-top:1px solid rgba(255,255,255,0.05); margin:0.5rem 0 1.25rem;" />
            <div style="font-size:0.8rem; color:#334155; line-height:1.8; padding: 0 0.25rem;">
                <span style="color:#475569; font-weight:600;">How to start</span><br/>
                1&nbsp; Pick a bot<br/>
                2&nbsp; Customize settings<br/>
                3&nbsp; Hit <em style="color:#38bdf8;">Start Session</em>
            </div>
            """, unsafe_allow_html=True)

    # ── Page header ─────────────────────────────────────────
    st.markdown("""
        <div style="text-align:center; padding:2rem 0 2.25rem;">
            <h1 style="font-size:2.4rem; font-weight:800; margin:0 0 0.5rem;
                       letter-spacing:-0.03em; line-height:1.15;">
                Choose Your Bot
            </h1>
            <p style="color:#475569; font-size:0.9rem; margin:0; font-weight:400;">
                Select a bot, configure its personality, and start your session
            </p>
        </div>
        """, unsafe_allow_html=True)

    # ── Card grid ────────────────────────────────────────────
    bot_meta = [
        {
            "name": "General",
            "icon": "🐾",
            "tagline": "Your friendly all-purpose AI assistant",
            "card_class": "card-general",
            "badge": "Versatile",
        },
        {
            "name": "ProfileExplainer",
            "icon": "📋",
            "tagline": "Analyze & explain professional profiles",
            "card_class": "card-profileexplainer",
            "badge": "Analytical",
        },
        {
            "name": "BoardGenie",
            "icon": "🎲",
            "tagline": "Create & manage project boards with flair",
            "card_class": "card-boardgenie",
            "badge": "Strategic",
        },
    ]

    col1, col2, col3 = st.columns(3, gap="large")
    for col, bot in zip([col1, col2, col3], bot_meta):
        with col:
            is_selected = st.session_state.selected_bot == bot["name"]
            sel_class = "card-selected" if is_selected else ""
            check = "✓" if is_selected else ""

            st.markdown(f"""
                <div class="bot-card {bot['card_class']} {sel_class}">
                    <div class="bot-card-check">{check}</div>
                    <div class="bot-card-badge">{bot['badge']}</div>
                    <div class="bot-card-icon">{bot['icon']}</div>
                    <div class="bot-card-name">{bot['name']}</div>
                    <div class="bot-card-tagline">{bot['tagline']}</div>
                </div>
                """, unsafe_allow_html=True)

            btn_label = "✓ Selected" if is_selected else "Select →"
            if st.button(btn_label, key=f"select_{bot['name']}",
                         use_container_width=True):
                st.session_state.selected_bot = bot["name"]
                st.session_state.selected_bot_widget = bot["name"]
                st.rerun()
    st.markdown("<hr/>", unsafe_allow_html=True)

    # ── Config section ───────────────────────────────────────
    selected_bot = st.session_state.selected_bot

    st.markdown(f"""
        <div style="margin-bottom:1.1rem;">
            <h3 style="color:#f1f5f9; font-size:1.05rem; font-weight:700;
                       margin:0 0 0.2rem; letter-spacing:-0.01em;">
                Configure {selected_bot}
            </h3>
            <p style="color:#475569; font-size:0.8rem; margin:0;">
                Customize your bot's personality and behaviour before starting
            </p>
        </div>
        """, unsafe_allow_html=True)

    return selected_bot
