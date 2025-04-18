import streamlit as st
import pandas as pd

st.title("📊 Analyse des Données")
uploaded_file = st.file_uploader("Importer un fichier CSV", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.success("Fichier chargé avec succès ✅")
    st.dataframe(df.head())
    st.write("### Statistiques")
    st.write(df.describe())