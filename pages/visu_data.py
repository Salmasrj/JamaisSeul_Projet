import streamlit as st
import pandas as pd
import plotly.express as px

st.title("📈 Visualisation Interactives")

uploaded_file = st.file_uploader("Importer un fichier CSV", type="csv", key="plot")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    col = st.selectbox("Choisir une colonne numérique à visualiser", df.select_dtypes("number").columns)
    fig = px.histogram(df, x=col, title=f"Distribution de {col}")
    st.plotly_chart(fig, use_container_width=True)