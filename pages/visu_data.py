import streamlit as st
import pandas as pd
import plotly.express as px

st.title("📈 Visualisations à partir du CSV")

uploaded_file = st.file_uploader("📤 Importer un fichier CSV", type="csv")

use_default = st.checkbox("Ou utiliser le fichier par défaut", value=True)

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.success("✅ CSV importé depuis l'upload")
elif use_default:
    df = pd.read_csv("data/donnees.csv")
    st.success("✅ CSV chargé depuis le dossier local")
else:
    st.warning("Veuillez importer un fichier ou utiliser le fichier local.")
    st.stop()

# Visualisation simple
numeric_cols = df.select_dtypes("number").columns

if not numeric_cols.empty:
    col = st.selectbox("Choisir une colonne numérique", numeric_cols)
    fig = px.histogram(df, x=col, title=f"Distribution de {col}")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.error("Aucune colonne numérique trouvée.")