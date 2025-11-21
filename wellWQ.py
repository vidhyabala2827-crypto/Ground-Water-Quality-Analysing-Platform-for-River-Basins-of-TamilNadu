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
    .css-1d391kg h2 {color: #0059b3;}
    </style>
""", unsafe_allow_html=True)

# -----------------
# App Title
# -----------------
st.markdown("<h1 style='text-align: center; color: #003366;'>Ground water quality Analysis- River Basins of TamilNadu</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; font-style: italic; color: #0059b3;'>\"We never know the worth of water till the well is dry\"</h4>", unsafe_allow_html=True)
st.markdown("<h5 style='text-align: center; color: #003366;'>- Thomas Fuller</h5>", unsafe_allow_html=True)

st.image(
    "https://images.unsplash.com/photo-1506744038136-46273834b3fb?ixlib=rb-4.0.3&auto=format&fit=crop&w=1500&q=80",
    use_container_width=True
)

# -----------------
# Load default data
# -----------------
@st.cache_data
def load_default_data():
    df = pd.read_csv("WQ_Basin.csv")
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df['Year'] = df['Date'].dt.year
    return df

df_default = load_default_data()
df = df_default.copy()

# -----------------
# Load user uploaded data
# -----------------
@st.cache_data
def load_data(file):
    if file.name.endswith('.csv'):
        df = pd.read_csv(file)
    else:
        df = pd.read_excel(file)
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df['Year'] = df['Date'].dt.year
    return df

# -----------------
# Sidebar buttons
# -----------------
help_clicked = st.sidebar.button("Help / About")
author_clicked = st.sidebar.button("Authors & Data Source")
upload_clicked = st.sidebar.button("Upload Data(Optional)")

# ⭐ ADDED USSL DIAGRAM OPTION HERE ⭐
menu = st.sidebar.selectbox(
    "Select Option",
    [
        "Select an option",
        "Descriptive Statistics",
        "Visualizations",
        "Correlation Analysis",
        "Diagrams"
    ]
)

# -----------------
# Display help if clicked
# -----------------
if help_clicked:
    st.subheader("Help / About")
    st.markdown("""
**Descriptive Statistics**
- Pick a basin and year range to view summaries  
- Stats available: mean, median, minimum_value, maximum_ value, standard_deviation, count  

**Visualizations**
- Compare parameters across years and seasons  
- Bar Chart, Scatter Plot, Box Plot, Line Graph  

**Correlation Analysis**
- Explore parameter relationships (Pearson, Spearman)  

**Upload Your Own Data**
- Optional CSV/Excel upload  
- Columns: Basin, Date (YYYY-MM-DD), Season, Latitude, Longitude, numeric parameters
""")

# -----------------
# Step-by-step selections
# -----------------
if menu != "Select an option":

    basins = df['Basin'].dropna().unique()
    basin = st.sidebar.selectbox("Select Basin", ["Select a Basin"] + list(basins))

    if basin != "Select a Basin":

        years = np.sort(df['Year'].dropna().astype(int))
        year_range = st.sidebar.slider(
            "Select Year Range",
            min_value=int(years.min()),
            max_value=int(years.max()),
            value=(int(years.min()), int(years.max()))
        )

        parameters = df.select_dtypes(include=[np.number]).columns.tolist()
        exclude_cols = ['OBJECTID_12', 'Latitude', 'Longitude', 'Year']
        parameters = [p for p in parameters if p not in exclude_cols]

        param = st.sidebar.selectbox("Select Parameter", ["Select a Parameter"] + parameters)

        if param != "Select a Parameter":

            filtered = df[(df['Basin']==basin) &
                          (df['Year']>=year_range[0]) &
                          (df['Year']<=year_range[1])]

            if filtered.empty:
                st.warning("No data for selected basin/year.")

            else:

                # -----------------
                # Descriptive Statistics
                # -----------------
                if menu == "Descriptive Statistics":

                    stat = st.sidebar.multiselect(
                        "Select Statistics",
                        ["mean","median","min","max","std","count"]
                    )

                    if stat:
                        st.subheader("Descriptive Statistics")
                        results = filtered.groupby(['Year','Season'])[param].agg(stat).reset_index()
                        st.dataframe(results)

                # -----------------
                # Visualizations
                # -----------------
                elif menu == "Visualizations":

                    viz_type = st.sidebar.selectbox(
                        "Select Visualization",
                        ["Select Visualization","Bar Chart","Scatter Plot","Box Plot","Line Graph"]
                    )

                    if viz_type != "Select Visualization":
                        st.subheader("Visualizations")
                        filtered['Year'] = filtered['Year'].astype(int)
                        plt.figure(figsize=(12,6))

                        if viz_type=="Bar Chart":
                            avg = filtered.groupby(['Year','Season'])[param].mean().reset_index()
                            sns.barplot(x="Year", y=param, hue="Season", data=avg)

                        elif viz_type=="Scatter Plot":
                            sns.scatterplot(x="Year", y=param, hue="Season", data=filtered)
                            sns.regplot(x="Year", y=param, data=filtered, scatter=False, color="red")

                        elif viz_type=="Box Plot":
                            sns.boxplot(x="Season", y=param, data=filtered)

                        elif viz_type=="Line Graph":
                            sns.lineplot(x="Year", y=param, hue="Season", marker="o", data=filtered)

                        plt.title(f"{viz_type} of {param} for {basin}")
                        plt.xticks(rotation=90)
                        st.pyplot(plt)

                # -----------------
                # Correlation Analysis
                # -----------------
                elif menu == "Correlation Analysis":

                    corr_method = st.sidebar.radio("Correlation Method", ["pearson","spearman"])
                    corr_df = filtered[parameters].dropna()
                    corr = corr_df.corr(method=corr_method)

                    st.subheader("Correlation Analysis")
                    st.dataframe(corr)

                    plt.figure(figsize=(12,8))
                    ax = sns.heatmap(corr, annot=True, cmap="coolwarm", vmin=-1,vmax=1)

                    st.pyplot(plt)

                # -----------------
                # ⭐ NEW SECTION — DIAGRAMS ⭐
                # -----------------
                elif menu == "Diagrams":

                    diagram_type = st.sidebar.selectbox(
                        "Select Diagram",
                        ["Select Diagram", "USSL Diagram"]
                    )

                    if diagram_type == "USSL Diagram":

                        st.subheader("USSL Diagram (C–S Classification)")

                        # -------- IMPORTS FOR DIAGRAM --------
                        import matplotlib.pyplot as plt
                        import matplotlib.gridspec as gridspec
                        import matplotlib.cm as cm
                        import numpy as np

                        df_temp = filtered.copy()

                        # ---------- SAR ----------
                        df_temp["Ca_meq"] = df_temp["Ca"] / 20.04
                        df_temp["Mg_meq"] = df_temp["Mg"] / 12.15
                        df_temp["Na_meq"] = df_temp["Na"] / 23.0
                        df_temp["SAR"] = df_temp["Na_meq"] / ((df_temp["Ca_meq"] + df_temp["Mg_meq"]) / 2) ** 0.5
                        df_temp["EC_raw"] = df_temp["EC"]

                        # ---------- EC Normalization ----------
                        def normalize_ec_for_plot(ec):
                            if ec < 250:
                                return (ec - 0) / 250 * 1
                            elif ec < 750:
                                return 1 + (ec - 250) / 500 * 1
                            elif ec < 2250:
                                return 2 + (ec - 750) / 1500 * 1
                            else:
                                return 3 + (ec - 2250) / (12000 - 2250) * 1

                        df_temp["EC_norm"] = df_temp["EC_raw"].apply(normalize_ec_for_plot)

                        # ---------- S-Lines ----------
                        m1 = (2.5 - 10.0) / 4
                        m2 = (6.5 - 18.0) / 4
                        m3 = (11.0 - 26.0) / 4
                        S1 = lambda x: m1 * x + 10
                        S2 = lambda x: m2 * x + 18
                        S3 = lambda x: m3 * x + 26

                        # ---------- Centroid ----------
                        def polygon_centroid(xs, ys):
                            x = np.array(xs); y = np.array(ys)
                            if x[0] != x[-1] or y[0] != y[-1]:
                                x = np.append(x, x[0]); y = np.append(y, y[0])
                            a = 0.5 * np.sum(x[:-1]*y[1:] - x[1:]*y[:-1])
                            if np.isclose(a, 0):
                                return x[:-1].mean(), y[:-1].mean()
                            cx = (1/(6*a)) * np.sum((x[:-1]+x[1:])*(x[:-1]*y[1:] - x[1:]*y[:-1]))
                            cy = (1/(6*a)) * np.sum((y[:-1]+y[1:])*(x[:-1]*y[1:] - x[1:]*y[:-1]))
                            return cx, cy

                        # ---------- Layout ----------
                        gs = gridspec.GridSpec(
                            3, 3,
                            width_ratios=[1.3, 8, 1],
                            height_ratios=[1, 9.5, 1.8],
                            wspace=0.05,
                            hspace=0.05
                        )

                        fig = plt.figure(figsize=(10, 9))

                        ax_left = fig.add_subplot(gs[1, 0])
                        ax_main = fig.add_subplot(gs[1, 1])
                        ax_bottom = fig.add_subplot(gs[2, 1])
                        ax_right = fig.add_subplot(gs[1, 2]); ax_right.axis("off")
                        ax_top = fig.add_subplot(gs[0, 1]); ax_top.axis("off")

                        # ---------- Plot Points ----------
                        villages = df_temp["Village"].unique()
                        import matplotlib.cm as cm
                        markers = ['o','s','D','^','v','<','>','p','h','*']
                        markers = markers * ((len(villages) // len(markers)) + 1)
                        cmap = cm.get_cmap('tab20', len(villages))

                        for i, v in enumerate(villages):
                            temp = df_temp[df_temp["Village"] == v]
                            ax_main.scatter(
                                temp["EC_norm"], temp["SAR"],
                                s=55,
                                marker=markers[i],
                                color=cmap(i),
                                edgecolors='black',
                                linewidths=1.0,
                                label=v
                            )

                        # ---------- Draw Lines ----------
                        ax_main.axvline(1, color='black')
                        ax_main.axvline(2, color='black')
                        ax_main.axvline(3, color='black')

                        xs = np.linspace(0, 4, 200)
                        ax_main.plot(xs, S1(xs), color='black')
                        ax_main.plot(xs, S2(xs), color='black')
                        ax_main.plot(xs, S3(xs), color='black')

                        ax_main.set_xlim(-0.05, 4.05)
                        ax_main.set_ylim(0, 40)

                        ax_main.set_xticks([0,1,2,3,4])
                        ax_main.set_xticklabels(["0","250","750","2250","12000"])

                        ax_main.set_xlabel("EC (µS/cm) at 25°C", fontsize=12, labelpad=80)
                        ax_main.set_ylabel("Sodium Adsorption Ratio (SAR)", fontsize=12, labelpad=80)

                        # ---------- Centroid Labels ----------
                        C_x = [0,1,2,3,4]
                        S_funcs = [lambda x: 0, S1, S2, S3, lambda x: 40]

                        for ci in range(1, 5):
                            xL = C_x[ci-1]; xR = C_x[ci]
                            for si in range(1, 5):
                                fB = S_funcs[si-1]; fT = S_funcs[si]
                                xs_poly = [xL, xR, xR, xL]
                                ys_poly = [fB(xL), fB(xR), fT(xR), fT(xL)]
                                cx, cy = polygon_centroid(xs_poly, ys_poly)
                                ax_main.text(
                                    cx, cy, f"C{ci}S{si}",
                                    ha="center", va="center",
                                    fontsize=9,
                                    bbox=dict(facecolor="white", edgecolor="black",
                                              boxstyle="round,pad=0.15")
                                )

                        # ---------- Legend ----------
                        ax_right.legend(
                            *ax_main.get_legend_handles_labels(),
                            title="Groundwater Samples",
                            loc='upper left',
                            fontsize=8,
                            frameon=True
                        )

                        fig.suptitle("USSL Diagram (C–S Classification)", fontsize=14)

                        st.pyplot(fig)

# -----------------
# Display Authors
# -----------------
if author_clicked:
    st.subheader("Authors & Data Source")
    st.markdown("""
- **B. Sridhanabharathi**, PhD Scholar (SWCE), AEC&RI, TNAU, Coimbatore  
- **V. Ravikumar**, Professor (SWCE), CWGS, TNAU, Coimbatore  
- **JC Kasimani**, CEO & Co-Founder, Infolayer, UK  

**Data Source:** Central Ground Water Board, Chennai
""")

# -----------------
# Upload Data
# -----------------
if upload_clicked:
    uploaded_file = st.file_uploader("Upload your own CSV/Excel (optional)", type=["csv","xls","xlsx"])
    if uploaded_file:
        df = load_data(uploaded_file)
        st.success("Your data is loaded! You can now use the selections above.")
