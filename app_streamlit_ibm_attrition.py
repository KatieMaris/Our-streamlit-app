import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os
st.set_page_config(page_title="IBM HR Attrition Explorer", layout="wide")
DATA_PATH = "WA_Fn-UseC_-HR-Employee-Attrition(in).csv"

@st.cache_data
def load_csv(path):
    try:
        return pd.read_csv(path)
    except Exception as e:
        st.error(f"⚠️ Error reading the default file: {e}")
        return None

def numeric_columns(df):
    return df.select_dtypes(include=[np.number]).columns.tolist()

def categorical_columns(df):
    return df.select_dtypes(include=['object', 'category']).columns.tolist()

def global_text_search(df, query, cols):
    if not query:
        return df
    q = query.lower()
    mask = pd.Series(False, index=df.index)
    for c in cols:
        mask = mask | df[c].astype(str).str.lower().str.contains(q, na=False)
    return df[mask]


if "started" not in st.session_state:
    st.session_state.started = False

if not st.session_state.started:
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        
        st.image("Analytics-in-HR.jpg", width='stretch')
        
        st.title("👋 Welcome to")
        st.title("IBM HR Attrition Explorer")
        st.markdown("---")
        st.markdown("""
        ### About this web:
        This dashboard is designed to help you analyze, visualize, and understand the core reasons behind employee turnover (Attrition) at IBM.
        
        **Key features:**
        *   📊 **Overview:** Attrition rates and income distribution.
        *   📈 **In-depth Analysis:** Correlations between age, gender, education field, and attrition.
        *   📋 **Data Table:** Flexible filtering and search functionality for employee information.
        """)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("🚀 Click here to start exploring", type="primary", width='stretch'):
            st.session_state.started = True
            st.rerun()
        


else:
    
    if st.sidebar.button("🏠 Back to Introduction page"):
        st.session_state.started = False
        st.rerun()
        
    st.sidebar.markdown("---")
    
   
    st.sidebar.title("⚙️ Control Panel")

    st.sidebar.header("1. Data Input")
    uploaded_file = st.sidebar.file_uploader("Upload CSV file", type=["csv"])

  
    df = None
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
        except Exception as e:
            st.sidebar.error(f"Error reading uploaded file: {e}")
            st.stop()
    else:
        if DATA_PATH and os.path.exists(DATA_PATH):
            df = load_csv(DATA_PATH)
            st.sidebar.success("Using default data path.")

   
    if df is None:
        st.info("👋 Please upload a CSV file on the sidebar or set the correct DATA_PATH in the source code.")
        st.stop()

   
    df.columns = df.columns.str.strip()
    num_cols = numeric_columns(df)
    cat_cols = categorical_columns(df)

   
    st.sidebar.header("2. Search & Filter")
    text_query = st.sidebar.text_input("🔍 Global search (keyword)")

    st.sidebar.markdown("---")
    
  
    gender_sel = st.sidebar.multiselect("Gender", options=sorted(df["Gender"].dropna().unique())) if "Gender" in df.columns else []
    edu_sel = st.sidebar.multiselect("Education Field", options=sorted(df["EducationField"].dropna().unique())) if "EducationField" in df.columns else []
    bt_sel = st.sidebar.multiselect("Business Travel", options=sorted(df["BusinessTravel"].dropna().unique())) if "BusinessTravel" in df.columns else []

    age_min, age_max = None, None
    if "Age" in df.columns:
        age_min_val, age_max_val = float(df["Age"].min()), float(df["Age"].max())
        if age_min_val < age_max_val:
            age_range = st.sidebar.slider("Age Range", min_value=age_min_val, max_value=age_max_val, value=(age_min_val, age_max_val), step=1.0)
            age_min, age_max = age_range
        else:
            st.sidebar.caption(f"Constant Age: {age_min_val}")
            age_min, age_max = age_min_val, age_max_val

    
    df_filtered = df.copy()

    if gender_sel:
        df_filtered = df_filtered[df_filtered["Gender"].isin(gender_sel)]
    if edu_sel:
        df_filtered = df_filtered[df_filtered["EducationField"].isin(edu_sel)]
    if bt_sel:
        df_filtered = df_filtered[df_filtered["BusinessTravel"].isin(bt_sel)]
    if age_min is not None and age_max is not None:
        df_filtered = df_filtered[(df_filtered["Age"] >= age_min) & (df_filtered["Age"] <= age_max)]

    search_columns = cat_cols + num_cols
    df_filtered = global_text_search(df_filtered, text_query, search_columns)


    st.title("📊 IBM HR Attrition Explorer")
    st.caption("Use the Control Panel on the left sidebar to interact with the data across all tabs.")

    tab_overview, tab_visuals, tab_table = st.tabs(["📝 Overview", "📈 Visualizations", "📋 Data Table"])

    
    with tab_overview:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Original Data Overview")
            if "Attrition" in df.columns:
                attr_counts = df["Attrition"].value_counts().reset_index()
                attr_counts.columns = ["Attrition", "Count"]
                fig_pie = px.pie(attr_counts, names="Attrition", values="Count", title="Overall Attrition Rate", hole=0.4)
                st.plotly_chart(fig_pie, width='stretch')
                
        with col2:
            st.subheader("Original Income Distribution")
            if "MonthlyIncome" in df.columns:
                fig_hist = px.histogram(df, x="MonthlyIncome", nbins=40, title="Monthly Income Distribution", marginal="box")
                st.plotly_chart(fig_hist, width='stretch')

    
    with tab_visuals:
        st.header(f"Filtered Visualizations ({len(df_filtered)} records)")
        
        col_v1, col_v2 = st.columns(2)
        
        with col_v1:
            if "Gender" in df_filtered.columns and "Attrition" in df_filtered.columns:
                grp = df_filtered.groupby(["Gender", "Attrition"]).size().reset_index(name="count")
                fig = px.bar(grp, x="Gender", y="count", color="Attrition", barmode="group", title="Attrition by Gender")
                st.plotly_chart(fig, width='stretch')
            else:
                st.info("Missing 'Gender' or 'Attrition' column.")

        with col_v2:
            if "EducationField" in df_filtered.columns and "Attrition" in df_filtered.columns:
                grp = df_filtered.groupby(["EducationField", "Attrition"]).size().reset_index(name="count")
                fig2 = px.bar(grp, x="EducationField", y="count", color="Attrition", barmode="group", title="Attrition by Education Field")
                fig2.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig2, width='stretch')
            else:
                st.info("Missing 'EducationField' or 'Attrition' column.")

        st.markdown("---")
        col_v3, col_v4 = st.columns(2)

        with col_v3:
            if "MonthlyIncome" in df_filtered.columns:
                fig3 = px.box(df_filtered, y="MonthlyIncome", x="Attrition" if "Attrition" in df_filtered.columns else None, 
                              color="Attrition" if "Attrition" in df_filtered.columns else None, points="all", title="Income Distribution (Filtered)")
                st.plotly_chart(fig3,width='stretch')
            else:
                st.info("Missing 'MonthlyIncome' column.")

        with col_v4:
            filtered_num_cols = [c for c in num_cols if c in df_filtered.columns]
            if len(filtered_num_cols) > 1:
                corr = df_filtered[filtered_num_cols].corr()
                fig_corr = px.imshow(corr, text_auto=False, aspect="auto", color_continuous_scale="RdBu_r", title="Correlation Matrix (Numeric)")
                st.plotly_chart(fig_corr, width='stretch')
            else:
                st.info("Not enough numeric columns available for correlation matrix.")

   
    with tab_table:
        st.header("Detailed Data Table")
        st.metric(label="Filtered Records Count", value=len(df_filtered))
        st.dataframe(df_filtered.reset_index(drop=True), width='stretch')
