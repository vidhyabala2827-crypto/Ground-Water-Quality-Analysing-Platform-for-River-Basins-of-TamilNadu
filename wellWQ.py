import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Ground Water Quality Analysis – River Basins of Tamil Nadu",
    layout="wide"
)

# =========================================================
# SIDEBAR STYLE
# =========================================================
st.markdown("""
<style>
[data-testid="stSidebar"] {background-color: #e6f2ff;}
</style>
""", unsafe_allow_html=True)

# =========================================================
# SIDEBAR CONTROLS
# =========================================================
help_clicked = st.sidebar.button("Help / About")
author_clicked = st.sidebar.button("Authors & Data Source")
upload_clicked = st.sidebar.button("Upload Data (Optional)")

menu = st.sidebar.selectbox(
    "Select Option",
    ["Select an option", "Descriptive Statistics", "Visualizations", "Correlation Analysis"]
)

# =========================================================
# TITLE
# =========================================================
st.markdown(
    "<h1 style='text-align:center; color:#003366;'>"
    "Ground Water Quality Analysis – River Basins of Tamil Nadu"
    "</h1>",
    unsafe_allow_html=True
)

st.markdown(
    "<h4 style='text-align:center; font-style:italic; color:#0059b3;'>"
    "Project Work done under ICAR – AICRP – IWM, TNAU, Coimbatore."
    "</h4>",
    unsafe_allow_html=True
)

# =========================================================
# INTRO
# =========================================================
if menu == "Select an option":
    st.markdown("""
    <div style="text-align: justify; font-size: 17px; line-height: 1.6;">
    Groundwater quality data at well level were obtained from the Central Ground Water Board (CGWB),
    Chennai Regional Office under the ICAR – AICRP – Integrated Water Management (IWM) programme.
    <br><br>
    This platform enables basin-wise assessment of groundwater quality across major river basins
    of Tamil Nadu using long-term monitoring data.
    </div>
    """, unsafe_allow_html=True)

    st.image(
        "image.png",
        caption="Spatial distribution of groundwater quality across river basins of Tamil Nadu",
        use_container_width=True
    )

# =========================================================
# LOAD DATA – YEAR HARD FIX
# =========================================================
@st.cache_data
def load_default_data():
    df = pd.read_csv("WQ_Basins.csv")

    # Ensure Date is string
    df["Date"] = df["Date"].astype(str)

    # 🔥 HARD YEAR EXTRACTION (THIS IS THE FIX)
    df["Year"] = (
        df["Date"]
        .str.extract(r"(19\d{2}|20\d{2})")[0]
        .astype(float)
    )

    return df

df = load_default_data()

# =========================================================
# LOAD USER DATA (SAME FIX)
# =========================================================
@st.cache_data
def load_data(file):
    if file.name.endswith(".csv"):
        df = pd.read_csv(file)
    else:
        df = pd.read_excel(file)

    df["Date"] = df["Date"].astype(str)
    df["Year"] = (
        df["Date"]
        .str.extract(r"(19\d{2}|20\d{2})")[0]
        .astype(float)
    )

    return df

# =========================================================
# HELP
# =========================================================
if help_clicked:
    st.subheader("Help / About")
    st.markdown("""
- Descriptive Statistics  
- Visualizations  
- Correlation Analysis  
""")

# =========================================================
# MAIN ANALYSIS
# =========================================================
if menu != "Select an option":

    basins = sorted(df["Basin"].dropna().unique())
    basin = st.sidebar.selectbox("Select Basin", basins)

    years = sorted(df["Year"].dropna().unique())

    st.sidebar.write(f"**Data available up to:** {int(max(years))}")

    year_range = st.sidebar.slider(
        "Select Year Range",
        min_value=int(min(years)),
        max_value=int(max(years)),
        value=(int(min(years)), int(max(years)))
    )

    parameters = [
        c for c in df.select_dtypes(include=[np.number]).columns
        if c not in ["Year", "Latitude", "Longitude"]
    ]

    param = st.sidebar.selectbox("Select Parameter", parameters)

    filtered = df[
        (df["Basin"] == basin) &
        (df["Year"] >= year_range[0]) &
        (df["Year"] <= year_range[1])
    ]

    if filtered.empty:
        st.warning("No data available.")
    else:
        if menu == "Descriptive Statistics":
            st.subheader("Descriptive Statistics")
            st.dataframe(
                filtered.groupby(["Year", "Season"])[param]
                .agg(["mean", "median", "min", "max", "std", "count"])
                .reset_index()
            )

        elif menu == "Visualizations":
            st.subheader("Visualizations")
            plt.figure(figsize=(12,6))
            sns.lineplot(data=filtered, x="Year", y=param, hue="Season", marker="o")
            st.pyplot(plt)

        elif menu == "Correlation Analysis":
            st.subheader("Correlation Analysis")
            corr = filtered[parameters].corr()
            plt.figure(figsize=(12,8))
            sns.heatmap(corr, annot=True, cmap="coolwarm", vmin=-1, vmax=1)
            st.pyplot(plt)

# =========================================================
# AUTHORS
# =========================================================
if author_clicked:
    st.subheader("Authors & Data Source")
    st.markdown("""
- **B. Sridhanabharathi**, PhD Scholar, TNAU  
- **V. Ravikumar**, Professor, TNAU  

**Data Source:** CGWB, Government of India
""")

# =========================================================
# UPLOAD
# =========================================================
if upload_clicked:
    uploaded_file = st.file_uploader("Upload CSV / Excel", ["csv", "xls", "xlsx"])
    if uploaded_file:
        df = load_data(uploaded_file)
        st.success("Data loaded successfully.")
