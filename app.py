"""
app.py — Synapse Green-Truth Auditor · Streamlit Frontend
=========================================================
"""

import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from models.engine import load_databases, audit_product  # Fixed imports for your repo

# ─────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Synapse · Green-Truth Auditor",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────
# CSS - SYNAPSE THEME
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:ital,wght@0,300;0,400;0,500;0,600;1,300&display=swap');

html, body, [data-testid="stApp"], [data-testid="stHeader"], [data-testid="stMain"] {
    background-color: #F7F6F2 !important;
    color: #1A1A18 !important;
}

html, body, p, div, span, label, input, textarea, button {
    font-family: 'DM Sans', sans-serif !important;
}

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2.5rem 3rem 4rem !important; max-width: 1100px !important; }

/* Hero */
.hero-title {
    font-family: 'DM Serif Display', serif !important;
    font-size: 2.4rem; color: #1A1A18 !important;
    line-height: 1; display: flex; align-items: center; gap: 0.5rem;
}
.hero-badge {
    font-size: 0.65rem; font-weight: 700; letter-spacing: 0.14em;
    text-transform: uppercase; color: #2D6A4F; background: #E8F4F0;
    padding: 0.2rem 0.65rem; border-radius: 20px; margin-left: 0.4rem;
}
.hero-sub { color: #6B6B63 !important; font-size: 0.95rem; font-weight: 300; margin: 0.4rem 0 2rem; }

/* Score Card */
.score-card {
    background: #FFFFFF !important; border: 1.5px solid #E5E3DC;
    border-radius: 16px; padding: 1.6rem 1.8rem;
}
.score-number {
    font-family: 'DM Serif Display', serif !important;
    font-size: 3.8rem; line-height: 1; display: block;
}
.score-sub {
    font-size: 0.7rem; font-weight: 700; letter-spacing: 0.11em;
    text-transform: uppercase; color: #6B6B63; margin-bottom: 0.6rem;
}
.verdict-pill {
    display: inline-block; padding: 0.35rem 1.1rem; border-radius: 50px;
    font-size: 0.8rem; font-weight: 700; margin-top: 0.6rem; letter-spacing: 0.04em;
}
.pill-green { background: #E8F4F0; color: #2D6A4F; }
.pill-amber { background: #FEF3C7; color: #B45309; }
.pill-red   { background: #FEE2E2; color: #9B1C1C; }

/* Sentence rows */
.s-row {
    background:#FFFFFF !important; border:1.5px solid #E5E3DC;
    border-left:4px solid #E5E3DC; border-radius:10px; padding:1rem 1.2rem; margin-bottom:.55rem;
}
.s-text { font-size:.91rem; color:#1A1A18 !important; line-height:1.55; margin-bottom:.5rem; }
.v-tag { font-size:.65rem; font-weight:700; letter-spacing:.08em; text-transform:uppercase; padding:.18rem .55rem; border-radius:4px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# UI HELPERS
# ─────────────────────────────────────────────────────────────
VERDICT_META = {
    "Evidence-Based": {"icon":"📊", "tbg":"#DBEAFE","tfg":"#1E3A5F"},
    "Backed Claim": {"icon":"✅", "tbg":"#E8F4F0","tfg":"#2D6A4F"},
    "Vague": {"icon":"❌", "tbg":"#FEE2E2","tfg":"#9B1C1C"},
    "Uncertain / PR Speak": {"icon":"⚠️", "tbg":"#F3F4F6","tfg":"#4B5563"},
}

def scrape_url(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.content, 'html.parser')
        return soup.get_text(separator=' ', strip=True)[:2500]
    except: return None

# ─────────────────────────────────────────────────────────────
# DATA LOADING
# ─────────────────────────────────────────────────────────────
bcorp, gots, india = load_databases()

# ─────────────────────────────────────────────────────────────
# UI RENDER
# ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-title">
   🌿 Synapse Auditor <span class="hero-badge">InnoVision</span>
</div>
<p class="hero-sub">The Intent-Aware Sustainability Shopping Assistant.</p>
""", unsafe_allow_html=True)

input_tab = st.tabs(["🔗 URL Analyzer", "📝 Text Description"])
with input_tab[0]:
    url_input = st.text_input("Product URL", placeholder="https://example.com/product", label_visibility="collapsed")
with input_tab[1]:
    text_input = st.text_area("Product Text", placeholder="Paste description here...", height=150, label_visibility="collapsed")

if st.button("Run Audit ›", type="primary"):
    source = scrape_url(url_input) if url_input else text_input
    
    if source:
        with st.spinner("Analyzing claims..."):
            report = audit_product(source, bcorp, gots, india)
            sc = report["final_score"]
            ov = "Legitimate Claims" if sc > 0.7 else "Uncertain" if sc > 0.4 else "Greenwashing Likely"
            p_class = "pill-green" if sc > 0.7 else "pill-amber" if sc > 0.4 else "pill-red"

        # Display Score Card
        st.markdown(f"""
        <div class="score-card">
          <span class="score-sub">Credibility Score</span>
          <span class="score-number" style="color:#2D6A4F">{int(sc*100)}%</span>
          <span class="verdict-pill {p_class}">{ov}</span>
        </div>
        """, unsafe_allow_html=True)

        # Detailed Audit
        st.markdown("### 🕵️ Audit Trail")
        for r in report["sentences"]:
            m = VERDICT_META.get(r["verdict"], VERDICT_META["Uncertain / PR Speak"])
            st.markdown(f"""
            <div class="s-row">
              <div class="s-text">{r['sentence']}</div>
              <span class="v-tag" style="background:{m['tbg']};color:{m['tfg']}">{m['icon']} {r['verdict']}</span>
            </div>
            """, unsafe_allow_html=True)
