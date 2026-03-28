import streamlit as st
from models.engine import load_databases, audit_product # The direct connection

st.set_page_config(page_title="Green-Truth Engine", page_icon="🌿", layout="wide")

# Persistent Data Loading
bcorp, gots, india = load_databases()

st.title("🌿 Green-Truth Intervention Engine")
st.markdown("### AI-Powered Greenwashing Detection")

input_text = st.text_area("Analyze sustainability claims here:", height=150)

if st.button("Run Audit", type="primary") and input_text:
    # Handoff to the engine
    report = audit_product(input_text, bcorp, gots, india)
    score = report['final_score']

    # --- Visual Score Gauges ---
    st.divider()
    c1, c2 = st.columns([1, 2])
    
    with c1:
        if score < 0.4:
            color, label = "#FF4B4B", "Greenwashing Likely"
        elif score < 0.7:
            color, label = "#FFA500", "Uncertain / Mixed"
        else:
            color, label = "#00CC96", "Legitimate Claims"
            
        st.metric("Trust Score", f"{int(score * 100)}%", delta=label)
        
    with c2:
        st.write(f"### Status: {label}")
        st.progress(score)
        st.caption("This gauge measures the density of verifiable facts versus marketing 'fluff'.")

    # --- Brand Verification Cards ---
    if report["brands"]:
        st.subheader("🏢 Brand Integrity Check")
        b_cols = st.columns(len(report["brands"]))
        for i, m in enumerate(report["brands"]):
            with b_cols[i]:
                if m["certified"]: 
                    st.success(f"✅ **{m['brand']}**\n\nVerified {m['type']}")
                else: 
                    st.error(f"❌ **{m['brand']}**\n\nNo active certification")
