import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# -----------------
# Page Configuration
# -----------------
st.set_page_config(
    page_title="Ground Water Quality Analyzing Platform - Tamil Nadu Basins",
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
# Load User Data (No default)
# -----------------
@st.cache_data
def load_data(file):
    if file.name.endswith('WQ_Basin.csv'):
        df = pd.read_csv(file)
    else:
        df = pd.read_excel(file)
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df['Year'] = df['Date'].dt.year
    return df

# -----------------
# Sidebar Widgets
# -----------------
# Help button at top
help_clicked = st.sidebar.button("Help?")

# Main Menu
menu = st.sidebar.selectbox(
    "Select an option",
    ["Select an option", "Descriptive Statistics", "Visualizations", "Correlation Analysis"]
)

# Upload widget at bottom
st.sidebar.markdown("---")
st.sidebar.subheader("Upload Your Own Data (Optional)")
uploaded_file = st.sidebar.file_uploader(
    "Drag & drop a CSV/Excel file here", 
    type=["csv", "xls", "xlsx"]
)

if uploaded_file:
    df = load_data(uploaded_file)
else:
    df = None

# Authors button at bottom
st.sidebar.markdown("---")
show_authors = st.sidebar.button("Authors & Data Source")

# -----------------
# Show Help
# -----------------
if help_clicked:
    st.subheader("Help / About")
    st.markdown("""
    **Descriptive Statistics**
    - Pick a basin and year range to view summaries  
    - Stats available: mean, median, min, max, std, count  

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
    - Use the widget at the bottom of the sidebar  
    - Supported file types: CSV, XLS, XLSX  
    - Columns must include:  
        - Basin  
        - Date (YYYY-MM-DD)  
        - Season  
        - Latitude  
        - Longitude  
        - Parameters (numeric columns like EC, TDS, Na, Ca, etc.)  
    """)

# -----------------
# Show Authors Info if clicked
# -----------------
if show_authors:
    st.subheader("Authors")
    st.markdown("""
    - **Er. B. Sridhanabharathi**, PhD Scholar (SWCE), AEC&RI, TNAU, Coimbatore  
    - **Dr. V. Ravikumar**, Professor (SWCE), CWGS, TNAU, Coimbatore  
    - **JC Kasimani**, CEO & Co-Founder, Infolayer, UK  
    """)
    st.subheader("Data Source")
    st.markdown("""
    - Central Ground Water Board, Chennai, Ministry of Water Resources, Government of India
    """)

# -----------------
# Only show analysis if user uploaded data and selected a menu option
# -----------------
if df is not None and menu != "Select an option":
    # Extract dynamic info
    basins = df['Basin'].dropna().unique()
    years = np.sort(df['Year'].dropna().astype(int))
    parameters = df.select_dtypes(include=[np.number]).columns.tolist()
    exclude_cols = ['OBJECTID_12', 'Latitude', 'Longitude', 'Year']
    parameters = [p for p in parameters if p not in exclude_cols]

    # Dynamic controls
    basin = st.sidebar.selectbox("Select Basin", basins)
    year_range = st.sidebar.slider(
        "Select Year Range",
        min_value=int(years.min()),
        max_value=int(years.max()),
        value=(int(years.min()), int(years.max())),
        step=1
    )
    param = st.sidebar.selectbox("Select Parameter", parameters)
    stat = st.sidebar.multiselect("Select Statistics", ["mean", "median", "min", "max", "std", "count"], default=["mean"])
    viz_type = st.sidebar.selectbox("Select Visualization", ["Bar Chart", "Scatter Plot", "Box Plot", "Line Graph"])
    corr_method = st.sidebar.radio("Select Correlation Method", ["pearson", "spearman"])

    # Filter by year
    def filter_by_year(df, year_range):
        start, end = year_range
        return df[(df['Year'] >= start) & (df['Year'] <= end)]

    # -----------------
    # Descriptive Statistics
    # -----------------
    if menu == "Descriptive Statistics":
        st.subheader("Descriptive Statistics")
        filtered = df[df['Basin'] == basin]
        filtered = filter_by_year(filtered, year_range)
        if not filtered.empty:
            results = filtered.groupby(['Year', 'Season'])[param].agg(stat).reset_index()
            st.write(f"{stat} of {param} for {basin} during selected year(s)")
            st.dataframe(results)
        else:
            st.warning("No data available for the selected basin and year(s).")

    # -----------------
    # Visualizations
    # -----------------
    elif menu == "Visualizations":
        st.subheader("Visualizations")
        filtered = df[df['Basin'] == basin]
        filtered = filter_by_year(filtered, year_range)
        if not filtered.empty:
            filtered['Year'] = filtered['Year'].astype(int)
            if viz_type == "Bar Chart":
                avg = filtered.groupby(['Year', 'Season'])[param].mean().reset_index()
                plt.figure(figsize=(12,6))
                sns.barplot(x="Year", y=param, hue="Season", data=avg)
                plt.title(f"Bar Chart of {param} for {basin}")
                plt.xticks(rotation=90)
                st.pyplot(plt)
            elif viz_type == "Scatter Plot":
                plt.figure(figsize=(12,6))
                sns.scatterplot(x="Year", y=param, hue="Season", data=filtered)
                sns.regplot(x="Year", y=param, data=filtered, scatter=False, color="red")
                plt.title(f"Scatter Plot of {param} for {basin}")
                plt.xticks(rotation=90)
                st.pyplot(plt)
            elif viz_type == "Box Plot":
                plt.figure(figsize=(10,6))
                sns.boxplot(x="Season", y=param, data=filtered)
                plt.title(f"Box Plot of {param} for {basin}")
                st.pyplot(plt)
            elif viz_type == "Line Graph":
                plt.figure(figsize=(12,6))
                sns.lineplot(x="Year", y=param, hue="Season", marker="o", data=filtered)
                plt.title(f"Line Graph of {param} for {basin}")
                plt.xticks(rotation=90)
                st.pyplot(plt)

    # -----------------
    # Correlation Analysis
    # -----------------
    elif menu == "Correlation Analysis":
        st.subheader("Correlation Analysis")
        filtered = df[df['Basin'] == basin]
        filtered = filter_by_year(filtered, year_range)
        if not filtered.empty:
            corr_df = filtered[parameters].dropna()
            corr = corr_df.corr(method=corr_method)
            st.write(f"{corr_method.capitalize()} Correlation Matrix for {basin} (selected year(s))")
            st.dataframe(corr)

            plt.figure(figsize=(12,8))
            ax = sns.heatmap(
                corr,
                annot=True,
                cmap="coolwarm",
                fmt=".2f",
                vmin=-1, vmax=1,
                cbar_kws={'label':'Correlation Strength'}
            )
            colorbar = ax.collections[0].colorbar
            colorbar.set_ticks([-1,-0.5,0,0.5,1])
            colorbar.set_ticklabels(['-1\nStrong Negative','Weak (-0.5)','0\nNo Correlation','Weak (+0.5)','+1\nStrong Positive'])
            st.pyplot(plt)
        else:
            st.warning("No data available for the selected basin and year(s).")

# -----------------
# If no data uploaded yet
# -----------------
elif df is None:
    st.warning("Please upload a CSV or Excel file to start analysis")

