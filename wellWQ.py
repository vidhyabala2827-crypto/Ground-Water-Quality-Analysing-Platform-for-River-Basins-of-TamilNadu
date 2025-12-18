import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# -----------------
# Page Configuration
# -----------------
st.set_page_config(
    page_title="Ground Water Quality Analysis of Tamil Nadu River Basins",
    layout="wide"
)

# -----------------
# Sidebar Style
# -----------------
st.markdown("""
<style>
[data-testid="stSidebar"] {background-color: #e6f2ff;}
</style>
""", unsafe_allow_html=True)

# =========================================================
# SIDEBAR CONTROLS (DEFINE ONCE — VERY IMPORTANT)
# =========================================================
help_clicked = st.sidebar.button("Help / About")
author_clicked = st.sidebar.button("Authors & Data Source")
upload_clicked = st.sidebar.button("Upload Data (Optional)")

menu = st.sidebar.selectbox(
    "Select Option",
    ["Select an option", "Descriptive Statistics", "Visualizations", "Correlation Analysis"]
)

# =========================================================
# APP TITLE
# =========================================================
st.markdown(
    "<h1 style='text-align: center; color: #003366;'>"
    "Ground Water Quality Analysis – River Basins of Tamil Nadu"
    "</h1>",
    unsafe_allow_html=True
)

st.markdown(
    "<h4 style='text-align: center; font-style: italic; color: #0059b3;'>"
    "Project Work done under ICAR – AICRP – IWM, TNAU, Coimbatore."
    "</h4>",
    unsafe_allow_html=True
)

# =========================================================
# INTRO SECTION (ONLY WHEN APP OPENS)
# =========================================================
if menu == "Select an option":
    st.markdown("""
    <div style="text-align: justify; font-size: 17px; line-height: 1.6;">
    Groundwater quality data at well level were obtained from the Central Ground Water Board (CGWB),
    Chennai Regional Office and the project is done under the ICAR – AICRP – Integrated Water Management (IWM) programme,
    TNAU, Coimbatore.
    <br><br>
    This platform is developed to facilitate basin-wise assessment of groundwater quality across
    major river basins of Tamil Nadu using long-term monitoring data. It enables users to explore
    spatial and temporal variations in key water quality parameters through interactive statistical
    summaries, visualizations, and correlation analysis.
    <br><br>
    The platform is intended to support researchers, planners, and students in understanding
    groundwater quality trends and their implications for sustainable water resources management.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.image(
        "image.png",
        caption="Spatial distribution of groundwater Water Quality Index (WQI) across river basins of Tamil Nadu",
        use_container_width=True
    )

# =========================================================
# LOAD DEFAULT DATA
# =========================================================
@st.cache_data
def load_default_data():
    df = pd.read_csv("WQ_Basins.csv")
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Year"] = df["Date"].dt.year
    return df

df = load_default_data()

# =========================================================
# LOAD USER DATA
# =========================================================
@st.cache_data
def load_data(file):
    if file.name.endswith(".csv"):
        df = pd.read_csv(file)
    else:
        df = pd.read_excel(file)
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Year"] = df["Date"].dt.year
    return df

# =========================================================
# HELP SECTION
# =========================================================
if help_clicked:
    st.subheader("Help / About")
    st.markdown("""
**Descriptive Statistics**
- Basin-wise and year-wise statistical summaries  

**Visualizations**
- Temporal and seasonal trends of water quality parameters  

**Correlation Analysis**
- Pearson and Spearman correlation analysis  

**Upload Data**
- Upload CSV or Excel files with Basin, Date, Season and numeric parameters
""")

# =========================================================
# MAIN ANALYSIS SECTION
# =========================================================
if menu != "Select an option":

    basins = sorted(df["Basin"].dropna().unique())
    basin = st.sidebar.selectbox("Select Basin", basins)

    years = np.sort(df["Year"].dropna().astype(int))
    year_range = st.sidebar.slider(
        "Select Year Range",
        min_value=int(years.min()),
        max_value=int(years.max()),
        value=(int(years.min()), int(years.max()))
    )

    parameters = df.select_dtypes(include=[np.number]).columns.tolist()
    exclude_cols = ["Latitude", "Longitude", "Year"]
    parameters = [p for p in parameters if p not in exclude_cols]

    param = st.sidebar.selectbox("Select Parameter", parameters)

    filtered = df[
        (df["Basin"] == basin) &
        (df["Year"] >= year_range[0]) &
        (df["Year"] <= year_range[1])
    ]

    if filtered.empty:
        st.warning("No data available for the selected options.")
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
            plt.figure(figsize=(12, 6))
            sns.lineplot(data=filtered, x="Year", y=param, hue="Season", marker="o")
            st.pyplot(plt)

        elif menu == "Correlation Analysis":
            st.subheader("Correlation Analysis")
            corr = filtered[parameters].corr()
            plt.figure(figsize=(12, 8))
            sns.heatmap(corr, annot=True, cmap="coolwarm", vmin=-1, vmax=1)
            st.pyplot(plt)

# =========================================================
# AUTHORS
# =========================================================
if author_clicked:
    st.subheader("Authors & Data Source")
    st.markdown("""
- **B. Sridhanabharathi**, PhD Scholar (SWCE), AEC&RI, TNAU, Coimbatore  
- **V. Ravikumar**, Professor (SWCE), CWGS, TNAU, Coimbatore  
- **JC Kasimani**, CEO & Co-Founder, Infolayer, UK  

**Data Source:** Central Ground Water Board (CGWB), Ministry of Water Resources, Government of India
""")

# =========================================================
# UPLOAD DATA
# =========================================================
if upload_clicked:
    uploaded_file = st.file_uploader(
        "Upload your own CSV / Excel file",
        type=["csv", "xls", "xlsx"]
    )
    if uploaded_file:
        df = load_data(uploaded_file)
        st.success("Data loaded successfully. Use the sidebar to begin analysis.")
