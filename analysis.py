import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load dataset
df = pd.read_csv("dataset/climate_change_dataset.csv")

st.set_page_config(page_title="Climate Change Analysis", layout="wide")

st.title("📈 Climate Change Data Analysis")

menu = st.sidebar.selectbox("Select Analysis", ["Univariate Analysis", "Bivariate Analysis"])

# Univariate Analysis
if menu == "Univariate Analysis":
    col = st.selectbox("Select Column", df.columns)
    st.subheader(f"📊 Univariate Analysis of {col}")
    st.write(df[col].describe())
    
    fig, ax = plt.subplots()
    if df[col].dtype in ['int64','float64']:
        sns.histplot(df[col], kde=True, ax=ax)
    else:
        df[col].value_counts().plot(kind="bar", ax=ax)
    st.pyplot(fig)

# Bivariate Analysis
elif menu == "Bivariate Analysis":
    col1 = st.selectbox("Select First Column", df.columns, key="col1")
    col2 = st.selectbox("Select Second Column", df.columns, key="col2")
    st.subheader(f"📊 Bivariate Analysis: {col1} vs {col2}")
    
    fig, ax = plt.subplots()
    if df[col1].dtype in ['int64','float64'] and df[col2].dtype in ['int64','float64']:
        sns.scatterplot(x=df[col1], y=df[col2], ax=ax)
    else:
        sns.boxplot(x=df[col1], y=df[col2], ax=ax)
    st.pyplot(fig)
