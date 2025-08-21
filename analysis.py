import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# =============================
# LOAD DATA
# =============================
st.set_page_config(page_title="Climate Change Analysis", layout="wide")
df = pd.read_csv("dataset/climate_change_dataset.csv")

st.title("📈 Climate Change Data Analysis (Interactive • Plotly)")

# Helper: identify dtypes robustly
def is_numeric(s):
    return pd.api.types.is_numeric_dtype(s)

def is_categorical(s):
    return pd.api.types.is_object_dtype(s) or pd.api.types.is_categorical_dtype(s)

# =============================
# SIDEBAR FILTERS
# =============================
st.sidebar.header("🔍 Global Filters")

# Year Filter
if "Year" in df.columns:
    years = sorted(df["Year"].dropna().unique().tolist())
    sel_years = st.sidebar.multiselect("Select Year(s)", years, default=years)
    if sel_years:
        df = df[df["Year"].isin(sel_years)]

# Country Filter
if "Country" in df.columns:
    countries = sorted(df["Country"].dropna().unique().tolist())
    sel_countries = st.sidebar.multiselect("Select Country(s)", countries, default=countries)
    if sel_countries:
        df = df[df["Country"].isin(sel_countries)]

# Numeric Filters (range sliders)
numeric_filters = {
    "Avg Temperature (°C)": "Temperature Range (°C)",
    "CO2 Emissions (Tons/Capita)": "CO₂ Emissions Range",
    "Sea Level Rise (mm)": "Sea Level Rise Range (mm)",
    "Rainfall (mm)": "Rainfall Range (mm)",
    "Population": "Population Range",
    "Renewable Energy (%)": "Renewable Energy (%) Range",
    "Extreme Weather Events": "Extreme Weather Events Range",
    "Forest Area (%)": "Forest Area (%) Range",
}

for col, label in numeric_filters.items():
    if col in df.columns and is_numeric(df[col]):
        cmin = float(np.nanmin(df[col]))
        cmax = float(np.nanmax(df[col]))
        if np.isfinite(cmin) and np.isfinite(cmax):
            rmin, rmax = st.sidebar.slider(label, cmin, cmax, (cmin, cmax))
            df = df[(df[col] >= rmin) & (df[col] <= rmax)]

# =============================
# ANALYSIS TYPE
# =============================
analysis_type = st.sidebar.radio("Select Analysis Type", ["Univariate Analysis", "Bivariate Analysis"])

# =============================
# UNIVARIATE ANALYSIS
# =============================
if analysis_type == "Univariate Analysis":
    col = st.selectbox("Select Column", df.columns)
    view = st.radio("Choose", ["Statistics", "Visualization"], horizontal=True)

    if view == "Statistics":
        st.subheader(f"📊 Univariate Statistics: {col}")
        if is_numeric(df[col]):
            st.write(f"- Count: {int(df[col].count())}")
            st.write(f"- Mean: {df[col].mean():.3f}")
            st.write(f"- Median: {df[col].median():.3f}")
            st.write(f"- Std Dev: {df[col].std():.3f}")
            st.write(f"- Min: {df[col].min()}")
            st.write(f"- Max: {df[col].max()}")
        else:
            st.write("**Category Counts:**")
            counts = df[col].value_counts(dropna=False)
            for k, v in counts.items():
                st.write(f"- {k}: {v}")

    else:  # Visualization
        st.subheader(f"📊 Univariate Visualization: {col}")
        if is_numeric(df[col]):
            fig = px.histogram(df, x=col, marginal="box", nbins=40)
            fig.update_layout(xaxis_title=col, yaxis_title="Count")
            st.plotly_chart(fig, use_container_width=True)
        else:
            vc = df[col].value_counts().reset_index()
            vc.columns = [col, "Count"]
            fig = px.bar(vc, x=col, y="Count")
            st.plotly_chart(fig, use_container_width=True)

# =============================
# BIVARIATE ANALYSIS
# =============================
else:
    col1 = st.selectbox("Select First Column", df.columns, key="biv_col1")
    col2 = st.selectbox("Select Second Column", df.columns, key="biv_col2")
    mode = st.radio("Show", ["Table", "Visualization"], horizontal=True)

    if col1 == col2:
        st.warning("Please select two different columns for bivariate analysis.")
    else:
        col1_num, col2_num = is_numeric(df[col1]), is_numeric(df[col2])
        col1_cat, col2_cat = is_categorical(df[col1]), is_categorical(df[col2])

        # Let user choose grouping keys for tables (default to Country & Year if present)
        group_candidates = [c for c in df.columns if is_categorical(df[c])]
        default_groups = [g for g in ["Country", "Year"] if g in group_candidates]
        if mode == "Table":
            group_keys = st.multiselect(
                "Group by (for tables)",
                group_candidates,
                default=default_groups
            )

        # =============================
        # NUM vs NUM
        # =============================
        if col1_num and col2_num:
            if mode == "Table":
                st.subheader(f"📊 Pivot Table: {col1} & {col2}")
                if group_keys:
                    pivot = pd.pivot_table(
                        df,
                        values=[col1, col2],
                        index=group_keys,
                        aggfunc=["mean", "median", "min", "max", "count"]
                    )
                else:
                    # No groups: show a one-row summary
                    pivot = df[[col1, col2]].agg(["mean", "median", "min", "max", "count"])
                st.dataframe(pivot)
            else:
                st.subheader(f"📈 Scatter: {col1} vs {col2}")
                color_key = "Country" if "Country" in df.columns else None
                hover = [k for k in ["Country", "Year"] if k in df.columns]
                try:
                    fig = px.scatter(
                        df, x=col1, y=col2, color=color_key,
                        hover_data=hover, trendline="ols"
                    )
                except Exception:
                    # Fallback if statsmodels isn't available
                    fig = px.scatter(df, x=col1, y=col2, color=color_key, hover_data=hover)
                # Helpful toggles for comparison
                c1, c2 = st.columns(2)
                with c1:
                    logx = st.checkbox("Log scale X", value=False)
                with c2:
                    logy = st.checkbox("Log scale Y", value=False)
                fig.update_xaxes(type="log" if logx else "linear")
                fig.update_yaxes(type="log" if logy else "linear")
                st.plotly_chart(fig, use_container_width=True)

        # =============================
        # CAT vs CAT
        # =============================
        elif col1_cat and col2_cat:
            if mode == "Table":
                st.subheader(f"📊 Crosstab: {col1} vs {col2}")
                ctab = pd.crosstab(df[col1], df[col2], margins=False)
                st.dataframe(ctab)
                # Also show row/column mins & maxes (counts) as quick reference
                st.markdown("**Row-wise min/max counts:**")
                row_mins = ctab.min(axis=1)
                row_maxs = ctab.max(axis=1)
                row_summary = pd.DataFrame({"min": row_mins, "max": row_maxs})
                st.dataframe(row_summary)

                st.markdown("**Column-wise min/max counts:**")
                col_mins = ctab.min(axis=0)
                col_maxs = ctab.max(axis=0)
                col_summary = pd.DataFrame({"min": col_mins, "max": col_maxs})
                st.dataframe(col_summary)
            else:
                st.subheader(f"🧊 Heatmap: {col1} vs {col2}")
                ctab = pd.crosstab(df[col1], df[col2])
                fig = px.imshow(ctab, text_auto=True, aspect="auto", color_continuous_scale="Blues")
                st.plotly_chart(fig, use_container_width=True)

        # =============================
        # NUM vs CAT (either way around)
        # =============================
        else:
            # Determine which is which
            cat_col = col1 if col1_cat else col2
            num_col = col2 if col1_cat else col1

            if mode == "Table":
                st.subheader(f"📊 Grouped Summary of {num_col} by {cat_col}")
                # If user picked extra grouping keys, include them (but keep cat_col first)
                group_cols = [cat_col] + [g for g in (group_keys if mode == "Table" else []) if g != cat_col]
                grouped = df.groupby(group_cols, dropna=False)[num_col].agg(["mean", "median", "min", "max", "std", "count"])
                st.dataframe(grouped)
            else:
                st.subheader(f"📦 Box Plot: {num_col} by {cat_col}")
                fig = px.box(df, x=cat_col, y=num_col, color=cat_col)
                st.plotly_chart(fig, use_container_width=True)

# =============================
# TIPS FOR SCATTER COMPARISON
# =============================
with st.expander("💡 Tips: Make scatter comparisons clearer"):
    st.markdown(
        "- Use **Table** mode to see min/max/mean first, then switch to **Visualization**.\n"
        "- Toggle **log scales** if the axes are on very different ranges (e.g., Population vs Emissions).\n"
        "- Use the **hover** tooltips to compare exact points (Country/Year).\n"
        "- Zoom into dense regions to reduce overlap.\n"
        "- Color by **Country** (auto) to separate clusters."
    )
