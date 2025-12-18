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
        "Water Quality Indices"
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
    major river basins of Tamil Nadu using long-term monitoring data. It enables users to explore
    spatial and temporal variations in key water quality parameters through interactive statistical
    summaries, visualizations, correlation analysis, and water quality indices.
    </div>
    """, unsafe_allow_html=True)

    st.image(
        "image.png",
        caption="Spatial distribution of groundwater quality across river basins of Tamil Nadu",
        use_container_width=True
    )

# =========================================================
# LOAD DATA – YEAR HARD FIX (KEEPING YOUR WORKING FILE)
# =========================================================
@st.cache_data
def load_default_data():
    df = pd.read_csv("WQ_Basins.csv")
    df["Date"] = df["Date"].astype(str)
    df["Year"] = (
        df["Date"]
        .str.extract(r"(19\d{2}|20\d{2})")[0]
        .astype(float)
    )
    return df

df = load_default_data()

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
- Water Quality Indices (SAR, RSC, Na%, PI, MH, KR, PS, WQI)
""")

# =========================================================
# WATER QUALITY INDICES (COPIED AS-IS FROM YOUR REFERENCE)
# =========================================================
if menu == "Water Quality Indices":

    st.subheader("Water Quality Indices")
    st.markdown(
        "If water quality parameters are in **mg/L**, conversion to **meq/L** "
        "is handled internally for index calculations."
    )

    with st.expander("Show formulas and definitions", expanded=False):

        st.markdown("### **1. Sodium Adsorption Ratio (SAR)**")
        st.latex(r"SAR = \frac{Na^+}{\sqrt{\frac{Ca^{2+} + Mg^{2+}}{2}}}")

        st.markdown("### **2. Residual Sodium Carbonate (RSC)**")
        st.latex(r"RSC = (CO_3^{2-} + HCO_3^{-}) - (Ca^{2+} + Mg^{2+})")

        st.markdown("### **3. Sodium Percentage (Na%)**")
        st.latex(r"\%Na = \frac{Na^+ + K^+}{Na^+ + K^+ + Ca^{2+} + Mg^{2+}} \times 100")

        st.markdown("### **4. Permeability Index (PI)**")
        st.latex(r"PI = \frac{Na^+ + \sqrt{HCO_3^-}}{Ca^{2+} + Mg^{2+} + Na^+} \times 100")

        st.markdown("### **5. Magnesium Hazard (MH)**")
        st.latex(r"MH = \frac{Mg^{2+}}{Ca^{2+} + Mg^{2+}} \times 100")

        st.markdown("### **6. Kelly's Ratio (KR)**")
        st.latex(r"KR = \frac{Na^+}{Ca^{2+} + Mg^{2+}}")

        st.markdown("### **7. Potential Salinity (PS)**")
        st.latex(r"PS = Cl^- + \sqrt{SO_4^{2-}}")

        st.markdown("## 🔷 Water Quality Index (WQI) — Horton Method")
        st.latex(r"WQI = \frac{\sum (q_n \cdot W_n)}{\sum W_n}")

    unit_choice = st.radio("Select input unit:", ["meq/L", "mg/L"], index=0)

    df_wqi = df.copy()

    eq = {
        "Ca": 20.04, "Mg": 12.15, "Na": 23.0, "K": 39.1,
        "HCO3": 61.0, "CO3": 30.0, "Cl": 35.45, "SO4": 48.0
    }

    def to_meq(ion):
        if ion not in df_wqi.columns:
            return None
        x = pd.to_numeric(df_wqi[ion], errors="coerce")
        return x / eq[ion] if unit_choice == "mg/L" else x

    Na, Ca, Mg = to_meq("Na"), to_meq("Ca"), to_meq("Mg")
    K = to_meq("K")
    HCO3, CO3 = to_meq("HCO3"), to_meq("CO3")
    Cl, SO4 = to_meq("Cl"), to_meq("SO4")

    df_wqi["SAR"] = Na / np.sqrt((Ca + Mg) / 2)
    df_wqi["RSC"] = (CO3 + HCO3) - (Ca + Mg)
    df_wqi["Na%"] = ((Na + K) / (Na + K + Ca + Mg)) * 100
    df_wqi["PI"] = ((Na + np.sqrt(HCO3)) / (Ca + Mg + Na)) * 100
    df_wqi["MH"] = (Mg / (Ca + Mg)) * 100
    df_wqi["KR"] = Na / (Ca + Mg)
    df_wqi["PS"] = Cl + np.sqrt(SO4)

    Sn = {"SAR":10,"RSC":2.5,"Na%":60,"PI":25,"MH":50,"KR":1,"PS":3}
    k = 1 / sum(1 / v for v in Sn.values())
    W = {i: k / Sn[i] for i in Sn}

    df_wqi["WQI"] = sum(((df_wqi[i] / Sn[i]) * 100) * W[i] for i in Sn) / sum(W.values())

    df_wqi["WQI_Category"] = pd.cut(
        df_wqi["WQI"],
        bins=[0, 25, 50, 75, 100, 1e6],
        labels=["Excellent", "Good", "Poor", "Very Poor", "Unsuitable"]
    )

    st.dataframe(df_wqi)
    st.download_button(
        "Download Full Data with WQI",
        df_wqi.to_csv(index=False).encode("utf-8"),
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
