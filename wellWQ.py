import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Ground Water Quality Analysis – Tamil Nadu River Basins",
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
# SIDEBAR CONTROLS (DEFINE ONCE)
# =========================================================
help_clicked = st.sidebar.button("Help / About")
author_clicked = st.sidebar.button("Authors & Data Source")
upload_clicked = st.sidebar.button("Upload Data (Optional)")

menu = st.sidebar.selectbox(
    "Select Option",
    [
        "Descriptive Statistics",
        "Visualizations",
        "Correlation Analysis",
        "WQI Calculation"
    ]
)

# =========================================================
# APP TITLE
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
# INTRO SECTION
# =========================================================
if menu == "Select an option":
    st.markdown("""
    <div style="text-align: justify; font-size: 17px; line-height: 1.6;">
    Groundwater quality data at well level were obtained from the Central Ground Water Board (CGWB),
    Chennai Regional Office, and the project is under the ICAR – AICRP – Integrated Water Management (IWM) programme.
    <br><br>
    This platform enables basin-wise assessment of groundwater quality across major river basins
    of Tamil Nadu using long-term monitoring data. It supports statistical analysis, visualization,
    correlation assessment, and calculation of key water quality indices including the Water
    Quality Index (WQI).
    </div>
    """, unsafe_allow_html=True)

    st.image(
        "image.png",
        caption="Spatial distribution of groundwater Water Quality Index (WQI) across river basins of Tamil Nadu",
        use_container_width=True
    )

# =========================================================
# LOAD DATA
# =========================================================
@st.cache_data
def load_default_data():
    df = pd.read_csv("WQ_Basins.csv")
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Year"] = df["Date"].dt.year
    return df

df = load_default_data()

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
# HELP
# =========================================================
if help_clicked:
    st.subheader("Help / About")
    st.markdown("""
- **Descriptive Statistics**: Basin-wise and seasonal summaries  
- **Visualizations**: Trend and distribution plots  
- **Correlation Analysis**: Parameter relationships  
- **WQI Calculation**: SAR, RSC, Na%, PI, MH, KR, PS, and WQI (Horton method)
""")

# =========================================================
# WQI CALCULATION MODULE
# =========================================================
if menu == "WQI Calculation":

    st.subheader("Water Quality Indices & WQI (Horton Method)")

    unit_choice = st.radio("Select input unit:", ["meq/L", "mg/L"], index=0)

    df_wqi = df.copy()
    eq = {"Ca": 20, "Mg": 12.2, "Na": 23, "K": 39.1,
          "HCO3": 61, "CO3": 30, "Cl": 35.5, "SO4": 48}

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
    k = 1 / sum(1/v for v in Sn.values())
    W = {i: k/Sn[i] for i in Sn}

    df_wqi["WQI"] = sum(((df_wqi[i]/Sn[i])*100)*W[i] for i in Sn) / sum(W.values())

    df_wqi["WQI_Category"] = pd.cut(
        df_wqi["WQI"],
        bins=[0,25,50,75,100,1e6],
        labels=["Excellent","Good","Poor","Very Poor","Unsuitable"]
    )

    show_cols = ["Basin","Year","SAR","RSC","Na%","PI","MH","KR","PS","WQI","WQI_Category"]
    show_cols = [c for c in show_cols if c in df_wqi.columns]

    st.dataframe(df_wqi[show_cols])

    st.download_button(
        "Download WQI Results",
        df_wqi[show_cols].to_csv(index=False).encode("utf-8"),
        "WQI_results.csv"
    )

# =========================================================
# OTHER ANALYSIS MODULES
# =========================================================
if menu in ["Descriptive Statistics", "Visualizations", "Correlation Analysis"]:

    basins = sorted(df["Basin"].dropna().unique())
    basin = st.sidebar.selectbox("Select Basin", basins)

    years = np.sort(df["Year"].dropna().astype(int))
    yr = st.sidebar.slider("Select Year Range", int(years.min()), int(years.max()),
                           (int(years.min()), int(years.max())))

    parameters = [c for c in df.select_dtypes(include=[np.number]).columns
                  if c not in ["Latitude","Longitude","Year"]]

    param = st.sidebar.selectbox("Select Parameter", parameters)

    filtered = df[(df["Basin"]==basin) & (df["Year"]>=yr[0]) & (df["Year"]<=yr[1])]

    if menu == "Descriptive Statistics":
        st.subheader("Descriptive Statistics")
        st.dataframe(
            filtered.groupby(["Year","Season"])[param]
            .agg(["mean","median","min","max","std","count"])
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
- **JC Kasimani**, Infolayer, UK  

**Data Source:** Central Ground Water Board (CGWB), Government of India
""")

# =========================================================
# UPLOAD
# =========================================================
if upload_clicked:
    file = st.file_uploader("Upload CSV / Excel", ["csv","xls","xlsx"])
    if file:
        df = load_data(file)
        st.success("Data uploaded successfully.")

