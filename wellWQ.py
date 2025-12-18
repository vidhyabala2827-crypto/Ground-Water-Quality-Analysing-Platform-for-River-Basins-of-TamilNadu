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
    [
        "Select an option",
        "Descriptive Statistics",
        "Visualizations",
        "Correlation Analysis",
        "Water Quality Indicators"
    ]
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
    Chennai Regional Office and the project is done under the ICAR – AICRP – Integrated Water Management (IWM) programme,
    TNAU, Coimbatore.
    <br><br>
    This platform is developed to facilitate basin-wise assessment of groundwater quality across
    major river basins of Tamil Nadu using long-term monitoring data.
    </div>
    """, unsafe_allow_html=True)

    st.image(
        "image.png",
        caption="Spatial distribution of groundwater quality across river basins of Tamil Nadu",
        use_container_width=True
    )

# =========================================================
# LOAD DATA
# =========================================================
@st.cache_data
def load_default_data():
    df = pd.read_csv("WQ_Basins.csv")
    df["Date"] = df["Date"].astype(str)
    df["Year"] = df["Date"].str.extract(r"(19\d{2}|20\d{2})")[0].astype(float)
    return df

df = load_default_data()

@st.cache_data
def load_data(file):
    if file.name.endswith(".csv"):
        df = pd.read_csv(file)
    else:
        df = pd.read_excel(file)
    df["Date"] = df["Date"].astype(str)
    df["Year"] = df["Date"].str.extract(r"(19\d{2}|20\d{2})")[0].astype(float)
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
- Water Quality Indicators
""")

# =========================================================
# WATER QUALITY INDICATORS
# =========================================================
if menu == "Water Quality Indicators":

    st.subheader("Water Quality Indicators")

    unit_choice = st.radio("Select input unit:", ["meq/L", "mg/L"], index=0)

    indicators_options = ["SAR", "RSC", "Na%", "PI", "MH", "KR", "PS", "WQI"]
    selected_indicators = st.multiselect(
        "Select indicators to display:",
        indicators_options,
        default=indicators_options
    )

    df_wqi = df.copy()

    eq = {"Ca": 20, "Mg": 12.2, "Na": 23, "K": 39.1, "HCO3": 61, "CO3": 30, "Cl": 35.5, "SO4": 48}

    def to_meq(ion):
        if ion not in df_wqi.columns:
            return None
        x = pd.to_numeric(df_wqi[ion], errors="coerce")
        return x / eq[ion] if unit_choice == "mg/L" else x

    Na = to_meq("Na")
    Ca = to_meq("Ca")
    Mg = to_meq("Mg")
    K = to_meq("K")
    HCO3 = to_meq("HCO3")
    CO3 = to_meq("CO3")
    Cl = to_meq("Cl")
    SO4 = to_meq("SO4")

    if "SAR" in selected_indicators:
        df_wqi["SAR"] = Na / np.sqrt((Ca + Mg) / 2)

    if "RSC" in selected_indicators:
        df_wqi["RSC"] = (CO3 + HCO3) - (Ca + Mg)

    if "Na%" in selected_indicators:
        df_wqi["Na%"] = ((Na + K) / (Na + K + Ca + Mg)) * 100

    if "PI" in selected_indicators:
        df_wqi["PI"] = ((Na + np.sqrt(HCO3)) / (Ca + Mg + Na)) * 100

    if "MH" in selected_indicators:
        df_wqi["MH"] = (Mg / (Ca + Mg)) * 100

    if "KR" in selected_indicators:
        df_wqi["KR"] = Na / (Ca + Mg)

    if "PS" in selected_indicators:
        df_wqi["PS"] = Cl + np.sqrt(SO4)

    if "WQI" in selected_indicators:
        df_wqi["WQI"] = df_wqi[selected_indicators].mean(axis=1)

    # ---- Clean & show table ----
    df_display = df_wqi.copy()

    round_cols = ["SAR", "RSC", "Na%", "PI", "MH", "KR", "PS", "WQI"]
    for col in round_cols:
        if col in df_display.columns:
            df_display[col] = df_display[col].round(2)

    st.dataframe(df_display)
    st.download_button(
        "Download Full Data",
        df_display.to_csv(index=False).encode("utf-8"),
        "WQ_full_with_WQI.csv"
    )
    st.stop()

# =========================================================
# OTHER ANALYSIS MODULES
# =========================================================
if menu in ["Descriptive Statistics", "Visualizations", "Correlation Analysis"]:

    basins = sorted(df["Basin"].dropna().unique())
    basin = st.sidebar.selectbox("Select Basin", basins)

    years = sorted(df["Year"].dropna().astype(int))
    yr = st.sidebar.slider(
        "Select Year Range",
        int(min(years)),
        int(max(years)),
        (int(min(years)), int(max(years)))
    )

    parameters = [
        c for c in df.select_dtypes(include=[np.number]).columns
        if c not in ["Year", "Latitude", "Longitude"]
    ]

    param = st.sidebar.selectbox("Select Parameter", parameters)

    filtered = df[
        (df["Basin"] == basin) &
        (df["Year"] >= yr[0]) &
        (df["Year"] <= yr[1])
    ]

    if menu == "Descriptive Statistics":
        st.subheader("Descriptive Statistics")
        st.dataframe(
            filtered.groupby(["Year", "Season"])[param]
            .agg(["mean", "median", "min", "max", "std"])
            .reset_index()
        )

    elif menu == "Visualizations":

        viz = st.sidebar.selectbox(
            "Select Visualization",
            ["Select Visualization", "Bar Chart", "Scatter Plot", "Box Plot", "Line Graph"]
        )

        if viz != "Select Visualization":

            units = {
                "Ca": "mg/L", "Mg": "mg/L", "Na": "mg/L", "K": "mg/L",
                "Cl": "mg/L", "SO4": "mg/L", "EC": "µS/cm",
                "Na%": "%", "PI": "%", "MH": "%"
            }

            ylabel = f"{param} ({units.get(param,'')})" if units.get(param) else param

            filtered_plot = filtered.copy()
            filtered_plot["Year"] = filtered_plot["Year"].astype(int)

            plt.figure(figsize=(12, 6))

            if viz == "Bar Chart":
                sns.barplot(
                    x="Year",
                    y=param,
                    hue="Season",
                    data=filtered_plot.groupby(["Year", "Season"], as_index=False)[param].mean()
                )
            elif viz == "Scatter Plot":
                sns.scatterplot(x="Year", y=param, hue="Season", data=filtered_plot)
                sns.regplot(x="Year", y=param, data=filtered_plot, scatter=False, color="red")
            elif viz == "Box Plot":
                sns.boxplot(x="Season", y=param, data=filtered_plot)
            elif viz == "Line Graph":
                sns.lineplot(x="Year", y=param, hue="Season", marker="o", data=filtered_plot)

            plt.xlabel("Year")
            plt.ylabel(ylabel)
            plt.xticks(rotation=90)
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
- **B. Sridhanabharathi**, PhD Scholar (SWCE), TNAU  
- **V. Ravikumar**, Professor (SWCE), TNAU  
**Data Source:** CGWB, Chennai
""")

# =========================================================
# UPLOAD
# =========================================================
if upload_clicked:
    file = st.file_uploader("Upload CSV / Excel", ["csv", "xls", "xlsx"])
    if file:
        df = load_data(file)
        st.success("File uploaded successfully.")
