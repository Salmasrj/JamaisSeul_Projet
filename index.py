import streamlit as st
from streamlit_lottie import st_lottie
import json

st.set_page_config(
    page_title="Data App",
    page_icon="📊",
    layout="wide"
)

# Charger animation Lottie
def load_lottiefile(path: str):
    with open(path, "r") as f:
        return json.load(f)

lottie_anim = load_lottiefile("assets/data.json")

# UI
st.markdown("""
    <style>
        .big-title {font-size: 3rem; font-weight: 700;}
        .sub-title {font-size: 1.5rem; color: #6c757d;}
    </style>
""", unsafe_allow_html=True)

col1, col2 = st.columns([1, 1])
with col1:
    st.markdown("<div class='big-title'>Bienvenue dans l'app d'analyse de données 📊</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-title'>Explorez, analysez et visualisez vos données facilement</div>", unsafe_allow_html=True)
    st.markdown("### 🚀 Fonctionnalités")
    st.markdown("- Import de CSV\n- Analyse statistique\n- Visualisations dynamiques\n- UI claire et moderne")

with col2:
    st_lottie(lottie_anim, height=300, key="data")

st.markdown("---")
st.info("👉 Commencez en utilisant le menu à gauche !")