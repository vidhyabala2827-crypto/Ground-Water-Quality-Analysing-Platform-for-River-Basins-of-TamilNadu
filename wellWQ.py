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
    major river basins of Tamil Nadu using long-term monitoring data. It enables users to explore
    spatial and temporal variations in key water quality parameters through interactive statistical
    summaries, visualizations, and correlation analysis.
    <br><br>
    The platform is intended to support researchers, planners, and students in understanding
    groundwater quality trends and their implications for sustainable water resources management.
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
# WATER QUALITY INDICATORS (COPIED AS-IS FROM YOUR REFERENCE)
# =========================================================
if menu == "Water Quality Indicators":
    st.subheader("Water Quality Indicators")
    st.markdown("If water quality parameters are in mg/L, conversion to meq/L is handled internally for index calculations.")

    
    with st.expander("Show formulas and definitions", expanded=False):
        st.markdown("### **1. Sodium Adsorption Ratio (SAR)**")
        st.latex(r"SAR = \frac{Na^+}{\sqrt{\frac{Ca^{2+} + Mg^{2+}}{2}}}")
        st.markdown("Indicates sodium hazard. High SAR reduces soil permeability.")

        st.markdown("---")
        st.markdown("### **2. Residual Sodium Carbonate (RSC)**")
        st.latex(r"RSC = (CO_3^{2-} + HCO_3^{-}) - (Ca^{2+} + Mg^{2+})")
        st.markdown("High RSC suggests carbonate/bicarbonate hazard.")

        st.markdown("---")
        st.markdown("### **3. Sodium Percentage (Na%)**")
        st.latex(r"\%Na = \frac{Na^+ + K^+}{Na^+ + K^+ + Ca^{2+} + Mg^{2+}} \times 100")
        st.markdown("Indicates sodium dominance. High Na% affects soil structure.")

        st.markdown("---")
        st.markdown("### **4. Permeability Index (PI)**")
        st.latex(r"PI = \frac{Na^+ + \sqrt{HCO_3^-}}{Ca^{2+} + Mg^{2+} + Na^+} \times 100")
        st.markdown("Indicates long-term impact on soil permeability.")

        st.markdown("---")
        st.markdown("### **5. Magnesium Hazard (MH)**")
        st.latex(r"MH = \frac{Mg^{2+}}{Ca^{2+} + Mg^{2+}} \times 100")
        st.markdown("High MH can reduce crop yield.")

        st.markdown("---")
        st.markdown("### **6. Kelly's Ratio (KR)**")
        st.latex(r"KR = \frac{Na^+}{Ca^{2+} + Mg^{2+}}")
        st.markdown("KR > 1 indicates unsuitability for irrigation.")

        st.markdown("---")
        st.markdown("### **7. Potential Salinity (PS)**")
        st.latex(r"PS = Cl^- + \sqrt{SO_4^{2-}}")
        st.markdown("Represents salinity hazard.")

        st.markdown("---")
        st.markdown("## 🔷 Water Quality Index (WQI) — Horton Method")
        st.latex(r"WQI = \frac{\sum (q_n \cdot W_n)}{\sum W_n}")
        st.latex(r"q_n = \left( \frac{V_n - V_{id}}{S_n - V_{id}} \right) \times 100")
        st.latex(r"W_n = \frac{k}{S_n}")
        st.latex(r"k = \frac{1}{\sum (1 / S_n)}")
        st.markdown("Vid = 0 for all indices.")
        Sn_table = pd.DataFrame({"Index": ["SAR","RSC","Na%","PI","MH","KR","PS"], "Standard Limit (Sₙ)": [10,2.5,60,25,50,1,3]})
        st.dataframe(Sn_table, hide_index=True)

    unit_choice = st.radio("Select input unit:", ["meq/L", "mg/L"], index=0)

    indicators_options = ["SAR", "RSC", "Na%", "PI", "MH", "KR", "PS", "WQI"]
    selected_indicators = st.multiselect("Select indicators to display:", indicators_options, default=indicators_options)

    df_wqi = df.copy()
    eq = {"Ca": 20, "Mg": 12.2, "Na": 23, "K": 39.1, "HCO3": 61, "CO3": 30, "Cl": 35.5, "SO4": 48}

    def to_meq(ion):
        if ion not in df_wqi.columns: return None
        x = pd.to_numeric(df_wqi[ion], errors="coerce")
        return x / eq[ion] if unit_choice == "mg/L" else x

    need = {"SAR":["Na","Ca","Mg"],"RSC":["CO3","HCO3","Ca","Mg"],"Na%":["Na","K","Ca","Mg"],
            "PI":["Na","HCO3","Ca","Mg"],"MH":["Ca","Mg"],"KR":["Na","Ca","Mg"],"PS":["Cl","SO4"]}

    for idx in ["SAR","RSC","Na%","PI","MH","KR","PS"]:
        if idx not in selected_indicators or idx in df_wqi.columns: continue
        if any(i not in df_wqi.columns for i in need[idx]): continue
        Na, Ca, Mg, K = to_meq("Na"), to_meq("Ca"), to_meq("Mg"), to_meq("K")
        HCO3, CO3, Cl, SO4 = to_meq("HCO3"), to_meq("CO3"), to_meq("Cl"), to_meq("SO4")
        if idx == "SAR": df_wqi["SAR"] = Na / np.sqrt((Ca + Mg) / 2)
        elif idx == "RSC": df_wqi["RSC"] = (CO3 + HCO3) - (Ca + Mg)
        elif idx == "Na%": df_wqi["Na%"] = ((Na + K) / (Na + K + Ca + Mg)) * 100
        elif idx == "PI": df_wqi["PI"] = ((Na + np.sqrt(HCO3)) / (Ca + Mg + Na)) * 100
        elif idx == "MH": df_wqi["MH"] = (Mg / (Ca + Mg)) * 100
        elif idx == "KR": df_wqi["KR"] = Na / (Ca + Mg)
        elif idx == "PS": df_wqi["PS"] = Cl + np.sqrt(SO4)

   
    Sn = {"SAR":10,"RSC":2.5,"Na%":60,"PI":25,"MH":50,"KR":1,"PS":3}
    usable = [i for i in Sn if i in df_wqi.columns]
    if usable:
        k = 1 / sum([1/Sn[i] for i in usable])
        W = {i: k/Sn[i] for i in usable}
        for i in usable: df_wqi[f"q_{i}"] = (df_wqi[i] / Sn[i]) * 100
        for i in usable: df_wqi[f"W_{i}"] = df_wqi[f"q_{i}"] * W[i]
        df_wqi["WQI"] = df_wqi[[f"W_{i}" for i in usable]].sum(axis=1) / sum(W.values())

        def classify(x):
            return ("Excellent" if x <= 25 else
                    "Good" if x <= 50 else
                    "Poor" if x <= 75 else
                    "Very Poor" if x <= 100 else
                    "Unsuitable")
        df_wqi["WQI_Category"] = df_wqi["WQI"].apply(classify)

    
    # ---- Clean & show table ----
    df_display = df_wqi.drop(
        columns=[c for c in df_wqi.columns if c.startswith("q_") or c.startswith("W_")],
        errors="ignore"
    )
    index_cols = [i for i in indicators_options if i in df_display.columns and i != "WQI"]
    ordered = [c for c in df_display.columns if c not in index_cols + ["WQI","WQI_Category"]] + index_cols + ["WQI","WQI_Category"]

# ===== ROUND WATER QUALITY INDICATORS (DISPLAY ONLY) =====
    round_cols = ["SAR", "RSC", "Na%", "PI", "MH", "KR", "PS", "WQI"]

    for col in round_cols:
        if col in df_display.columns:
            df_display[col] = df_display[col].round(2)


    st.dataframe(df_display[ordered])

    st.download_button("Download Full Data", df_display.to_csv(index=False).encode("utf-8"), "WQ_full_with_WQI.csv")
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
        corr = filtered[parameters].dropna().corr(method=st.sidebar.radio("Correlation Method", ["pearson","spearman"]))
        st.subheader("Correlation Matrix")
        st.dataframe(corr)
        plt.figure(figsize=(12,8))
        sns.heatmap(corr, annot=True, cmap="coolwarm", vmin=-1, vmax=1)
        st.pyplot(plt)
        plt.yticks(rotation=0)
        st.pyplot(plt)
            

# =========================================================
# AUTHORS
# =========================================================
if author_clicked:
    st.subheader("Authors & Data Source")
    st.markdown("""
- **B. Sridhanabharathi**, PhD Scholar (SWCE), TNAU, E-Mail ID - vidhyabala2827@gmail.com  
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






