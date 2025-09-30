import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# -----------------
# Page Configuration
# -----------------
st.set_page_config(
    page_title="Ground Water Quality Analyzer - Tamil Nadu Basins",
    layout="wide"
)

# -----------------
# Sidebar Custom Style
# -----------------
st.markdown(
    """
    <style>
    [data-testid="stSidebar"] {background-color: #e6f2ff;}
    .css-1d391kg h2 {color: #0059b3;}
    </style>
    """,
    unsafe_allow_html=True
)

# -----------------
# App Title and Caption
# -----------------
st.markdown("<h1 style='text-align: center; color: #003366;'>Well Water Quality Analyzer - Tamil Nadu Basins</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; font-style: italic; color: #0059b3;'>\"We never know the worth of water till the well is dry\"</h4>", unsafe_allow_html=True)
st.markdown("<h5 style='text-align: center; color: #003366;'>- Thomas Fuller</h5>", unsafe_allow_html=True)

# -----------------
# Banner Image
# -----------------
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
# Load user uploaded data (optional)
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
# Sidebar Top: Help Button
# -----------------
help_clicked = st.sidebar.button("Help?")

if help_clicked:
    st.subheader("Help / About")
    st.markdown("""
**Descriptive Statistics**
- Pick a basin and year range to view summaries  
- Stats available: mean, median, minimum_value, maximum_value, standard_deviation, count  

**Visualizations**
- Compare parameters across years and seasons  
- Bar Chart: average parameter by year & season  
- Scatter Plot: individual points and trends, regression line  
- Box Plot: distribution of parameter across seasons  
- Line Graph: trends of parameter over time  

**Correlation Analysis**
- Explore how parameters are related  
- Methods: Pearson (linear), Spearman (rank-based)  
- Output: correlation table + heatmap  

**Upload Your Own Data (Optional)**
- Supported file types: CSV, XLS, XLSX  
- Columns must include: Basin, Date (YYYY-MM-DD), Season, Latitude, Longitude, numeric parameters (EC, TDS, Na, Ca, etc.)
""")

# -----------------
# Sidebar Step 1: Select Option
# -----------------
menu = st.sidebar.selectbox(
    "Select an option",
    ["Select an option", "Descriptive Statistics", "Visualizations", "Correlation Analysis"]
)

# Step-by-step selection only if menu is selected
if menu != "Select an option":
    basins = df['Basin'].dropna().unique()
    basin = st.sidebar.selectbox("Select Basin", ["Select a Basin"] + list(basins))

    if basin != "Select a Basin":
        years = np.sort(df['Year'].dropna().astype(int))
        year_range = st.sidebar.slider(
            "Select Year Range",
            min_value=int(years.min()),
            max_value=int(years.max()),
            value=(int(years.min()), int(years.max())),
            step=1
        )

        parameters = df.select_dtypes(include=[np.number]).columns.tolist()
        exclude_cols = ['OBJECTID_12', 'Latitude', 'Longitude', 'Year']
        parameters = [p for p in parameters if p not in exclude_cols]
        param = st.sidebar.selectbox("Select Parameter", ["Select a Parameter"] + parameters)

        if param != "Select a Parameter":
            filtered = df[(df['Basin'] == basin) & (df['Year'] >= year_range[0]) & (df['Year'] <= year_range[1])]
            if filtered.empty:
                st.warning("No data available for the selected basin and year(s).")
            else:
                season_palette = {"Pre-Monsoon": "#1f77b4", "Post-Monsoon": "#ff7f0e"}

                if menu == "Descriptive Statistics":
                    stat = st.sidebar.multiselect(
                        "Select Statistics",
                        ["mean", "median", "min", "max", "std", "count"]
                    )
                    if stat:
                        st.subheader("Descriptive Statistics")
                        results = filtered.groupby(['Year', 'Season'])[param].agg(stat).reset_index()
                        st.write(f"{stat} of {param} for {basin} during selected year(s)")
                        st.dataframe(results)

                elif menu == "Visualizations":
                    viz_type = st.sidebar.selectbox(
                        "Select Visualization",
                        ["Select Visualization", "Bar Chart", "Scatter Plot", "Box Plot", "Line Graph"]
                    )
                    if viz_type != "Select Visualization":
                        st.subheader("Visualizations")
                        filtered['Year'] = filtered['Year'].astype(int)

                        if viz_type == "Bar Chart":
                            avg = filtered.groupby(['Year', 'Season'])[param].mean().reset_index()
                            plt.figure(figsize=(12,6))
                            sns.barplot(x="Year", y=param, hue="Season", data=avg, palette=season_palette)
                            plt.title(f"Bar Chart of {param} for {basin}")
                            plt.xticks(rotation=90)
                            st.pyplot(plt)

                        elif viz_type == "Scatter Plot":
                            plt.figure(figsize=(12,6))
                            sns.scatterplot(x="Year", y=param, hue="Season", data=filtered, palette=season_palette)
                            sns.regplot(x="Year", y=param, data=filtered, scatter=False, color="red")
                            plt.title(f"Scatter Plot of {param} for {basin}")
                            plt.xticks(rotation=90)
                            st.pyplot(plt)

                        elif viz_type == "Box Plot":
                            plt.figure(figsize=(10,6))
                            sns.boxplot(x="Season", y=param, data=filtered, palette=season_palette)
                            plt.title(f"Box Plot of {param} for {basin}")
                            st.pyplot(plt)

                        elif viz_type == "Line Graph":
                            plt.figure(figsize=(12,6))
                            sns.lineplot(x="Year", y=param, hue="Season", marker="o", data=filtered, palette=season_palette)
                            plt.title(f"Line Graph of {param} for {basin}")
                            plt.xticks(rotation=90)
                            st.pyplot(plt)

                elif menu == "Correlation Analysis":
                    corr_method = st.sidebar.radio("Select Correlation Method", ["pearson", "spearman"])
                    corr_df = filtered[parameters].dropna()
                    corr = corr_df.corr(method=corr_method)
                    st.subheader("Correlation Analysis")
                    st.write(f"{corr_method.capitalize()} Correlation Matrix for {basin} (selected year(s))")
                    st.dataframe(corr)

                    plt.figure(figsize=(12,8))
                    ax = sns.heatmap(
                        corr, annot=True, cmap="coolwarm", fmt=".2f",
                        vmin=-1, vmax=1, cbar_kws={'label':'Correlation Strength'}
                    )
                    colorbar = ax.collections[0].colorbar
                    colorbar.set_ticks([-1,-0.5,0,0.5,1])
                    colorbar.set_ticklabels(['-1\nStrong Negative','Weak (-0.5)','0\nNo Correlation','Weak (+0.5)','+1\nStrong Positive'])
                    st.pyplot(plt)

# -----------------
# Authors & Data Source (main page, always at bottom)
# -----------------
st.markdown("---")
st.subheader("Authors & Data Source")
st.markdown("""
- **Er. B. Sridhanabharathi**, PhD Scholar (SWCE), AEC&RI, TNAU, Coimbatore  
- **Dr. V. Ravikumar**, Professor (SWCE), CWGS, TNAU, Coimbatore  
- **JC Kasimani**, CEO & Co-Founder, Infolayer, UK  

**Data Source:** Central Ground Water Board, Chennai, Ministry of Water Resources, Government of India
""")

# -----------------
# Upload your own file (optional, main page, always at bottom)
# -----------------
uploaded_file = st.file_uploader(
    "Upload your own CSV/Excel (optional)",
    type=["csv", "xls", "xlsx"]
)
if uploaded_file:
    df = load_data(uploaded_file)
    st.success("Your data is loaded! You can now use the selections above.")
