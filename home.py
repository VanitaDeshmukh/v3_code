# Home.py
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Climate Dataset - Home", layout="wide")

# Load dataset
@st.cache_data
def load_data():
    return pd.read_csv("dataset/climate_change_dataset.csv")

df = load_data()

# -----------------------------
# Page Title
# -----------------------------
st.title("🌍 Climate Change Dataset - Home")

st.markdown("""
### 📌 Project Objective
The goal of this project is to **analyze the Climate Change dataset** using Exploratory Data Analysis (EDA) 
and visualization techniques to uncover meaningful insights.
""")

# -----------------------------
# Sidebar Options
# -----------------------------
option = st.sidebar.selectbox(
    "Select Information to View",
    [
        "Dataset Preview",
        "Shape & Size",
        "Column Details",
        "Missing Values",
        "Unique Values",
        "Value Counts (per column)",
        "Full Dataset"
    ]
)

# -----------------------------
# Dataset Info Sections
# -----------------------------
if option == "Dataset Preview":
    st.subheader("🔎 Dataset Preview")
    st.dataframe(df.head())

elif option == "Shape & Size":
    st.subheader("📐 Dataset Shape & Size")
    st.write(f"**Rows:** {df.shape[0]}")
    st.write(f"**Columns:** {df.shape[1]}")

elif option == "Column Details":
    st.subheader("📊 Column Details")
    col_info = pd.DataFrame({
        "Data Type": df.dtypes,
        "Missing Values": df.isnull().sum(),
        "Unique Values": df.nunique()
    })
    st.dataframe(col_info)

elif option == "Missing Values":
    st.subheader("🚨 Missing Values Count")
    st.write(df.isnull().sum())

elif option == "Unique Values":
    st.subheader("🔑 Unique Values per Column")
    st.write(df.nunique())

elif option == "Value Counts (per column)":
    st.subheader("📊 Value Counts")
    col = st.selectbox("Select a column", df.columns)
    st.write(df[col].value_counts())

elif option == "Full Dataset":
    st.subheader("📝 Full Dataset")
    st.dataframe(df)

