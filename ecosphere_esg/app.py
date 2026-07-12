"""
EcoSphere ESG Management Platform — Streamlit Dashboard
Simulates data pulled from Odoo backend models (esg.emission.factor,
esg.carbon.transaction, esg.compliance.issue).
"""

import time

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="EcoSphere ESG",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global styles ────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background: linear-gradient(160deg, #0a0f1a 0%, #111827 40%, #0d1b2a 100%);
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
        border-right: 1px solid rgba(16, 185, 129, 0.15);
    }

    [data-testid="stSidebar"] .stRadio label {
        color: #e2e8f0 !important;
        font-weight: 500;
    }

    .hero-title {
        font-size: 2.4rem;
        font-weight: 800;
        background: linear-gradient(135deg, #10b981, #34d399, #6ee7b7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
        letter-spacing: -0.5px;
    }

    .hero-sub {
        color: #94a3b8;
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }

    .kpi-card {
        background: linear-gradient(145deg, rgba(30,41,59,0.9), rgba(15,23,42,0.95));
        border: 1px solid rgba(16, 185, 129, 0.2);
        border-radius: 16px;
        padding: 1.4rem 1.6rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        height: 100%;
    }

    .kpi-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 40px rgba(16, 185, 129, 0.15);
    }

    .kpi-label {
        color: #94a3b8;
        font-size: 0.82rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 0.5rem;
    }

    .kpi-value {
        font-size: 2rem;
        font-weight: 800;
        color: #f1f5f9;
        line-height: 1.1;
    }

    .kpi-delta-up {
        color: #34d399;
        font-size: 0.85rem;
        font-weight: 600;
        margin-top: 0.4rem;
    }

    .kpi-delta-down {
        color: #f87171;
        font-size: 0.85rem;
        font-weight: 600;
        margin-top: 0.4rem;
    }

    .kpi-icon {
        font-size: 1.6rem;
        float: right;
        opacity: 0.7;
    }

    .section-header {
        font-size: 1.5rem;
        font-weight: 700;
        color: #f1f5f9;
        margin: 1.5rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid rgba(16, 185, 129, 0.3);
    }

    .badge-card {
        background: linear-gradient(145deg, #1e293b, #0f172a);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 14px;
        padding: 1.2rem;
        text-align: center;
        transition: all 0.25s ease;
        cursor: pointer;
    }

    .badge-card:hover {
        border-color: #10b981;
        box-shadow: 0 0 24px rgba(16, 185, 129, 0.25);
        transform: scale(1.03);
    }

    .badge-emoji {
        font-size: 2.5rem;
        display: block;
        margin-bottom: 0.5rem;
    }

    .badge-name {
        color: #e2e8f0;
        font-weight: 700;
        font-size: 0.95rem;
    }

    .badge-holder {
        color: #64748b;
        font-size: 0.78rem;
        margin-top: 0.3rem;
    }

    .score-caption {
        text-align: center;
        color: #94a3b8;
        font-size: 0.9rem;
        margin-top: -0.5rem;
    }

    .data-source-tag {
        display: inline-block;
        background: rgba(16, 185, 129, 0.12);
        color: #34d399;
        font-size: 0.72rem;
        font-weight: 600;
        padding: 0.2rem 0.6rem;
        border-radius: 20px;
        border: 1px solid rgba(16, 185, 129, 0.25);
        margin-bottom: 1rem;
    }

    div[data-testid="stMetric"] {
        background: linear-gradient(145deg, rgba(30,41,59,0.9), rgba(15,23,42,0.95));
        border: 1px solid rgba(16, 185, 129, 0.2);
        border-radius: 16px;
        padding: 1rem 1.2rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    }

    div[data-testid="stMetric"] label {
        color: #94a3b8 !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        font-size: 0.78rem !important;
    }

    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #f1f5f9 !important;
        font-weight: 800 !important;
        font-size: 1.8rem !important;
    }

    div[data-testid="stMetric"] [data-testid="stMetricDelta"] {
        font-weight: 600 !important;
    }

    .stButton > button {
        background: linear-gradient(135deg, #059669, #10b981) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        padding: 0.6rem 2rem !important;
        transition: all 0.2s ease !important;
    }

    .stButton > button:hover {
        box-shadow: 0 0 20px rgba(16, 185, 129, 0.4) !important;
        transform: translateY(-1px) !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ── Mock Odoo backend data ───────────────────────────────────────────────────
@st.cache_data
def load_emission_factors() -> pd.DataFrame:
    """Simulates esg.emission.factor records from Odoo."""
    return pd.DataFrame(
        {
            "name": ["Fleet Fuel", "Manufacturing", "Electricity", "Business Travel", "Waste Disposal"],
            "carbon_value": [2.31, 0.85, 0.42, 0.19, 1.12],
            "unit": ["kg CO₂/L", "kg CO₂/unit", "kg CO₂/kWh", "kg CO₂/km", "kg CO₂/kg"],
        }
    )


@st.cache_data
def load_carbon_transactions() -> pd.DataFrame:
    """Simulates esg.carbon.transaction records from Odoo."""
    return pd.DataFrame(
        {
            "name": ["Q1 Fleet Usage", "Plant Line A", "HQ Electricity", "Sales Travel", "Warehouse Ops"],
            "activity_amount": [4200, 18500, 96000, 12400, 7300],
            "emission_factor": ["Fleet Fuel", "Manufacturing", "Electricity", "Business Travel", "Manufacturing"],
            "total_emissions": [9702.0, 15725.0, 40320.0, 2356.0, 6205.0],
        }
    )


@st.cache_data
def load_compliance_issues() -> pd.DataFrame:
    """Simulates esg.compliance.issue records from Odoo."""
    return pd.DataFrame(
        {
            "name": ["ISO 14001 Audit", "Scope 3 Disclosure", "Waste Permit Renewal", "Safety Inspection"],
            "owner": ["Sarah Chen", "James Okonkwo", "Maria Lopez", "David Kim"],
            "due_date": ["2026-03-15", "2026-04-01", "2026-02-28", "2026-05-10"],
            "status": ["Resolved", "Open", "Overdue", "Open"],
        }
    )


@st.cache_data
def load_employee_badges() -> pd.DataFrame:
    """Mock gamification badge registry."""
    return pd.DataFrame(
        {
            "badge": [
                "Eco Pioneer",
                "Compliance Champion",
                "Carbon Crusher",
                "Green Leader",
                "Sustainability Star",
                "Audit Ace",
            ],
            "emoji": ["🌱", "🛡️", "♻️", "🏆", "⭐", "📋"],
            "employee": [
                "Sarah Chen",
                "James Okonkwo",
                "Maria Lopez",
                "David Kim",
                "Priya Sharma",
                "Alex Rivera",
            ],
            "points": [850, 720, 640, 590, 510, 480],
            "awarded": ["2026-01-12", "2026-02-03", "2026-01-28", "2026-02-14", "2026-03-01", "2026-02-20"],
        }
    )


def compute_kpis(transactions: pd.DataFrame, compliance: pd.DataFrame) -> dict:
    total_emissions = transactions["total_emissions"].sum()
    audits_done = (compliance["status"] == "Resolved").sum()
    audits_total = len(compliance)
    csr_participation = 87.4
    active_challenges = 12
    esg_score = min(100, round(
        40
        + (audits_done / max(audits_total, 1)) * 25
        + (csr_participation / 100) * 20
        + max(0, 15 - (total_emissions / 10000))
    ))
    return {
        "carbon_emissions": total_emissions,
        "carbon_delta": -8.3,
        "audits_done": audits_done,
        "audits_total": audits_total,
        "csr_participation": csr_participation,
        "csr_delta": 4.2,
        "active_challenges": active_challenges,
        "challenges_delta": 3,
        "esg_score": esg_score,
    }


def render_esg_gauge(score: int) -> None:
    """Circular progress gauge for the ESG Score."""
    color = "#10b981" if score >= 70 else "#f59e0b" if score >= 50 else "#ef4444"
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=score,
            number={"suffix": " / 100", "font": {"size": 42, "color": "#f1f5f9", "family": "Inter"}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": "#475569", "tickwidth": 1},
                "bar": {"color": color, "thickness": 0.25},
                "bgcolor": "rgba(30,41,59,0.6)",
                "borderwidth": 0,
                "steps": [
                    {"range": [0, 50], "color": "rgba(239,68,68,0.15)"},
                    {"range": [50, 70], "color": "rgba(245,158,11,0.15)"},
                    {"range": [70, 100], "color": "rgba(16,185,129,0.15)"},
                ],
                "threshold": {
                    "line": {"color": color, "width": 3},
                    "thickness": 0.8,
                    "value": score,
                },
            },
            title={"text": "ESG Score", "font": {"size": 22, "color": "#94a3b8", "family": "Inter"}},
        )
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=340,
        margin=dict(l=30, r=30, t=60, b=20),
        font={"family": "Inter"},
    )
    st.plotly_chart(fig, use_container_width=True)


def render_kpi_row(kpis: dict) -> None:
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            f"""
            <div class="kpi-card">
                <span class="kpi-icon">🌍</span>
                <div class="kpi-label">Carbon Emissions</div>
                <div class="kpi-value">{kpis['carbon_emissions']:,.0f}</div>
                <div class="kpi-delta-up">▼ {abs(kpis['carbon_delta'])}% vs last quarter</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
            <div class="kpi-card">
                <span class="kpi-icon">📋</span>
                <div class="kpi-label">Compliance Audits</div>
                <div class="kpi-value">{kpis['audits_done']}/{kpis['audits_total']}</div>
                <div class="kpi-delta-up">▲ {kpis['audits_done']} resolved</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            f"""
            <div class="kpi-card">
                <span class="kpi-icon">🤝</span>
                <div class="kpi-label">CSR Participation</div>
                <div class="kpi-value">{kpis['csr_participation']:.1f}%</div>
                <div class="kpi-delta-up">▲ {kpis['csr_delta']}% engagement</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col4:
        st.markdown(
            f"""
            <div class="kpi-card">
                <span class="kpi-icon">🎯</span>
                <div class="kpi-label">Active Challenges</div>
                <div class="kpi-value">{kpis['active_challenges']}</div>
                <div class="kpi-delta-up">▲ {kpis['challenges_delta']} new this month</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ── Load data ────────────────────────────────────────────────────────────────
emission_factors = load_emission_factors()
carbon_transactions = load_carbon_transactions()
compliance_issues = load_compliance_issues()
employee_badges = load_employee_badges()
kpis = compute_kpis(carbon_transactions, compliance_issues)

# ── Sidebar navigation ───────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🌿 EcoSphere")
    st.markdown(
        '<span style="color:#64748b;font-size:0.85rem;">ESG Management Platform</span>',
        unsafe_allow_html=True,
    )
    st.divider()
    page = st.radio(
        "Navigate",
        ["Executive Overview", "Environmental Tracking", "Gamification Hub"],
        label_visibility="collapsed",
    )
    st.divider()
    st.markdown(
        """
        <div style="color:#64748b;font-size:0.78rem;line-height:1.5;">
        <b style="color:#94a3b8;">Data Sources</b><br>
        esg.emission.factor<br>
        esg.carbon.transaction<br>
        esg.compliance.issue
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.divider()
    st.caption(f"Last synced: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}")

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown('<p class="hero-title">EcoSphere ESG Dashboard</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="hero-sub">Real-time sustainability intelligence · Powered by Odoo 18</p>',
    unsafe_allow_html=True,
)

render_kpi_row(kpis)
st.markdown("")

# ── Page routing ─────────────────────────────────────────────────────────────
if page == "Executive Overview":
    st.markdown('<p class="section-header">Executive Overview</p>', unsafe_allow_html=True)
    st.markdown('<span class="data-source-tag">Odoo · Aggregated KPIs</span>', unsafe_allow_html=True)

    col_left, col_right = st.columns([1, 1])

    with col_left:
        render_esg_gauge(kpis["esg_score"])
        rating = "Excellent" if kpis["esg_score"] >= 80 else "Good" if kpis["esg_score"] >= 60 else "Needs Attention"
        st.markdown(
            f'<p class="score-caption">Overall rating: <b style="color:#34d399;">{rating}</b></p>',
            unsafe_allow_html=True,
        )

    with col_right:
        st.markdown("#### Score Breakdown")
        st.metric("Environmental", f"{min(100, round(kpis['esg_score'] * 0.95))}", delta="2.1 pts")
        st.metric("Social (CSR)", f"{kpis['csr_participation']:.0f}%", delta=f"+{kpis['csr_delta']}%")
        st.metric("Governance", f"{round(kpis['audits_done'] / max(kpis['audits_total'], 1) * 100)}%", delta="1 audit pending")

        st.markdown("#### Recent Compliance Issues")
        st.dataframe(
            compliance_issues[["name", "owner", "status"]].rename(
                columns={"name": "Issue", "owner": "Owner", "status": "Status"}
            ),
            use_container_width=True,
            hide_index=True,
        )

    st.markdown("#### Carbon Transaction Summary")
    chart_col, table_col = st.columns([1, 1])
    with chart_col:
        fig_bar = go.Figure(
            go.Bar(
                x=carbon_transactions["name"],
                y=carbon_transactions["total_emissions"],
                marker_color=["#10b981", "#34d399", "#6ee7b7", "#059669", "#047857"],
                text=carbon_transactions["total_emissions"].apply(lambda v: f"{v:,.0f}"),
                textposition="outside",
            )
        )
        fig_bar.update_layout(
            title={"text": "Emissions by Activity", "font": {"color": "#e2e8f0", "size": 16}},
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font={"color": "#94a3b8"},
            xaxis={"tickangle": -25, "gridcolor": "rgba(71,85,105,0.3)"},
            yaxis={"title": "kg CO₂e", "gridcolor": "rgba(71,85,105,0.3)"},
            height=360,
            margin=dict(l=40, r=20, t=50, b=80),
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with table_col:
        st.dataframe(
            carbon_transactions.rename(
                columns={
                    "name": "Transaction",
                    "activity_amount": "Amount",
                    "emission_factor": "Factor",
                    "total_emissions": "Total CO₂e (kg)",
                }
            ),
            use_container_width=True,
            hide_index=True,
        )


elif page == "Environmental Tracking":
    st.markdown('<p class="section-header">Environmental Tracking</p>', unsafe_allow_html=True)
    st.markdown(
        '<span class="data-source-tag">Odoo · esg.emission.factor + esg.carbon.transaction</span>',
        unsafe_allow_html=True,
    )

    form_col, result_col = st.columns([1, 1])

    with form_col:
        st.markdown("#### Carbon Emission Calculator")
        with st.form("emission_calculator", clear_on_submit=False):
            activity_type = st.selectbox(
                "Activity Type",
                emission_factors["name"].tolist(),
                help="Select an emission factor from the Odoo master data.",
            )
            selected_factor = emission_factors.loc[
                emission_factors["name"] == activity_type, "carbon_value"
            ].values[0]
            selected_unit = emission_factors.loc[
                emission_factors["name"] == activity_type, "unit"
            ].values[0]

            st.info(f"Emission factor: **{selected_factor}** {selected_unit}")

            operational_amount = st.number_input(
                "Operational Amount",
                min_value=0.0,
                value=1000.0,
                step=100.0,
                format="%.2f",
            )
            submitted = st.form_submit_button("Calculate", use_container_width=True)

    with result_col:
        st.markdown("#### Emission Factor Registry")
        st.dataframe(
            emission_factors.rename(
                columns={"name": "Activity", "carbon_value": "Factor", "unit": "Unit"}
            ),
            use_container_width=True,
            hide_index=True,
        )

    if submitted:
        total = operational_amount * selected_factor
        progress = st.progress(0, text="Computing emissions…")
        for i in range(100):
            time.sleep(0.008)
            progress.progress(i + 1, text="Computing emissions…")
        progress.empty()

        st.toast(f"✅ Calculated: {total:,.2f} kg CO₂e", icon="🌿")

        st.success(
            f"**{activity_type}** · {operational_amount:,.2f} × {selected_factor} "
            f"= **{total:,.2f} kg CO₂e**"
        )

        result_fig = go.Figure(
            go.Indicator(
                mode="number+delta",
                value=total,
                number={"suffix": " kg CO₂e", "font": {"size": 48, "color": "#34d399"}},
                delta={"reference": total * 1.15, "relative": True, "valueformat": ".1%"},
                title={"text": "Total Carbon Emissions", "font": {"color": "#94a3b8", "size": 18}},
            )
        )
        result_fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=220,
            margin=dict(l=20, r=20, t=60, b=20),
        )
        st.plotly_chart(result_fig, use_container_width=True)

        st.markdown("##### Simulated Odoo Transaction Record")
        new_record = pd.DataFrame(
            [{
                "name": f"Calc · {activity_type}",
                "activity_amount": operational_amount,
                "emission_factor_id": activity_type,
                "total_emissions": round(total, 2),
            }]
        )
        st.dataframe(new_record, use_container_width=True, hide_index=True)


else:
    st.markdown('<p class="section-header">Gamification Hub</p>', unsafe_allow_html=True)
    st.markdown(
        '<span class="data-source-tag">Badge Auto-Award Engine · Click to celebrate!</span>',
        unsafe_allow_html=True,
    )

    st.markdown(
        "Click any badge below to trigger the **Badge Auto-Award** celebration. "
        "Employees earn badges through sustainability milestones and compliance achievements."
    )

    badge_cols = st.columns(3)
    for idx, row in employee_badges.iterrows():
        col = badge_cols[idx % 3]
        with col:
            st.markdown(
                f"""
                <div class="badge-card">
                    <span class="badge-emoji">{row['emoji']}</span>
                    <div class="badge-name">{row['badge']}</div>
                    <div class="badge-holder">{row['employee']} · {row['points']} pts</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button(f"Award {row['badge']}", key=f"badge_{idx}", use_container_width=True):
                st.session_state["last_awarded_badge"] = row["badge"]
                st.session_state["last_awarded_employee"] = row["employee"]
                st.session_state["trigger_celebration"] = True

    if st.session_state.get("trigger_celebration"):
        st.balloons()
        badge_name = st.session_state.get("last_awarded_badge", "Badge")
        employee = st.session_state.get("last_awarded_employee", "Employee")
        st.toast(f"🎉 Badge Auto-Award: {badge_name} → {employee}!", icon="🏆")
        st.success(f"**{badge_name}** automatically awarded to **{employee}**!")
        st.session_state["trigger_celebration"] = False

    st.divider()
    st.markdown("#### Leaderboard")
    leaderboard = employee_badges.sort_values("points", ascending=False).reset_index(drop=True)
    leaderboard.index += 1
    st.dataframe(
        leaderboard.rename(
            columns={
                "badge": "Badge",
                "employee": "Employee",
                "points": "Points",
                "awarded": "Awarded On",
            }
        ),
        use_container_width=True,
    )
