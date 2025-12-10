import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================
st.set_page_config(page_title="AI Usage & Academic Performance", layout="wide")

st.title("📊 Navigating Learning: AI Usage & Academic Performance")
st.markdown("### Interactive Analysis Dashboard")

# ==========================================
# 2. DATA LOADING & PROCESSING FUNCTION
# ==========================================
@st.cache_data
def load_data():
    file_path = "dataset.xlsx"
    try:
        # Load Excel file
        df = pd.read_excel(file_path, engine='openpyxl')
    except FileNotFoundError:
        st.error(f"File '{file_path}' not found. Please ensure it is in the same directory.")
        return None
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return None

    # --- PREPROCESSING (Combined from all notebooks) ---
    
    # 1. Clean Grade Column
    grade_col = "Current Year Average Grade:"
    if grade_col in df.columns:
        df[grade_col] = pd.to_numeric(df[grade_col], errors='coerce')
        # Create Inverted Grade for Correlation (Higher = Better)
        df['Performance_Target'] = df[grade_col] * -1
        
        # Create Grade Categories (For Pie Chart)
        def categorize_grade(grade):
            if pd.isna(grade): return "Unknown"
            elif grade <= 1.25: return "Excellent"
            elif grade <= 1.75: return "Very Good"
            elif grade <= 2.25: return "Good"
            elif grade <= 2.75: return "Fair"
            elif grade <= 3.00: return "Pass"
            else: return "Fail"
        df['Grade_Description'] = df[grade_col].apply(categorize_grade)

    # 2. Tool Columns (For Types_of_AI_Tools & ToolsAI)
    tool_cols = ['AI CHATBOT', 'AI FOR PROGRAMMING', 'WRITING ASSISTANT']
    valid_tools = [c for c in tool_cols if c in df.columns]
    for col in valid_tools:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # 3. Mode Columns (For Mode_of_Use & UseAI)
    mode_cols = ['Coding', 'Academic Assignment', 'Learning Support', 'Research']
    valid_modes = [c for c in mode_cols if c in df.columns]
    for col in valid_modes:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # 4. Predictor Columns (For obj5)
    predictors = [
        'General Perception of AI in Higher Education',
        'Current use of AI in Higher Education ',
        'Impact of AI on the Students Experience ',
        'Concern about the use of AI in higher education',
        'Future expectations of AI in higher education '
    ]
    for col in predictors:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    return df

# Load the data
df = load_data()

# Stop execution if data fails to load
if df is None:
    st.stop()

# ==========================================
# 3. SIDEBAR NAVIGATION
# ==========================================
st.sidebar.header("Navigation")
page = st.sidebar.radio("Select Analysis Module:", 
    ["1. Overview (Grade Distribution)", 
     "2. AI Usage Habits (Tools & Modes)", 
     "3. Impact Analysis (Correlations)"]
)

st.sidebar.markdown("---")
st.sidebar.info(f"**Total Respondents:** {len(df)}")
if st.sidebar.checkbox("Show Raw Data"):
    st.dataframe(df.head())

# ==========================================
# PAGE 1: OVERVIEW (Pie_Grade.ipynb)
# ==========================================
if page == "1. Overview (Grade Distribution)":
    st.header("1. Overview of Academic Performance")
    
    if 'Grade_Description' in df.columns:
        st.subheader("Distribution of Grades")
        
        # Prepare Data
        grade_counts = df['Grade_Description'].value_counts()
        
        # Visualization
        fig, ax = plt.subplots(figsize=(8, 8))
        colors = sns.color_palette('pastel')[0:len(grade_counts)]
        
        ax.pie(grade_counts, labels=grade_counts.index, autopct='%1.1f%%', 
               startangle=140, colors=colors, textprops={'fontsize': 12, 'fontweight': 'bold'})
        ax.set_title('Distribution of Academic Performance (Grade Description)', fontsize=16)
        
        st.pyplot(fig)
        
        st.markdown("""
        **Interpretation (from Pie_Grade.ipynb):**
        * **High Success Rate:** The chart is dominated by "Very Good" and "Good" ratings.
        * **High-Performing Cohort:** The respondents represent a capable group; AI usage is happening within the context of successful students, not failing ones.
        """)
    else:
        st.warning("Grade data not available.")

# ==========================================
# PAGE 2: USAGE HABITS (Types & Modes)
# ==========================================
elif page == "2. AI Usage Habits (Tools & Modes)":
    st.header("2. AI Usage Habits")
    
    tab1, tab2 = st.tabs(["A. Types of Tools", "B. Mode of Use"])
    
    # --- TAB 1: TYPES OF TOOLS (Types_of_AI_Tools.ipynb) ---
    with tab1:
        st.subheader("Prevalence of AI Tools")
        tool_cols = ['AI CHATBOT', 'AI FOR PROGRAMMING', 'WRITING ASSISTANT']
        valid_tools = [c for c in tool_cols if c in df.columns]
        
        if valid_tools:
            tool_counts = df[valid_tools].sum().sort_values(ascending=False)
            
            fig, ax = plt.subplots(figsize=(8, 5))
            sns.barplot(
                x=tool_counts.index, y=tool_counts.values, hue=tool_counts.index, 
                palette='viridis', legend=False, ax=ax
            )
            ax.set_ylabel("Count of Users")
            ax.set_xlabel("AI Tool Category")
            
            # Labels
            for i, v in enumerate(tool_counts.values):
                ax.text(i, v + 0.5, str(int(v)), ha='center', fontweight='bold')
                
            st.pyplot(fig)
            st.markdown("""
            **Insights (from Types_of_AI_Tools.ipynb):**
            * **Chatbot Dominance:** General chatbots are the primary interface.
            * **Simplicity:** Students prefer versatile tools over specialized ones.
            """)
    
    # --- TAB 2: MODE OF USE (Mode_of_Use.ipynb) ---
    with tab2:
        st.subheader("Primary Purpose of AI Usage")
        mode_cols = ['Coding', 'Academic Assignment', 'Learning Support', 'Research']
        valid_modes = [c for c in mode_cols if c in df.columns]
        
        if valid_modes:
            counts_df = df[valid_modes].apply(pd.Series.value_counts).T
            if 0 not in counts_df.columns: counts_df[0] = 0
            if 1 not in counts_df.columns: counts_df[1] = 0
            counts_df.columns = ['No', 'Yes']
            counts_df = counts_df.sort_values(by='Yes', ascending=False)
            
            fig, ax = plt.subplots(figsize=(10, 6))
            counts_df.plot(kind='bar', stacked=True, color=['#d9dddc', '#8BCC45'], ax=ax, width=0.7)
            ax.legend(title='Response', labels=['Non-User', 'User'])
            ax.set_xticklabels(counts_df.index, rotation=0)
            
            # Labels
            for c in ax.containers:
                ax.bar_label(c, label_type='center', fontweight='bold')
                
            st.pyplot(fig)
            st.markdown("""
            **Insights (from Mode_of_Use.ipynb):**
            * **Learning Support:** This is a top reason for usage, indicating students use AI as a "tutor."
            * **Balanced Use:** Once adopted, AI is applied broadly across coding, assignments, and research.
            """)

# ==========================================
# PAGE 3: IMPACT ANALYSIS (Correlations)
# ==========================================
elif page == "3. Impact Analysis (Correlations)":
    st.header("3. Impact on Academic Performance")
    st.info("Note: In these charts, a **Positive Correlation** means better grades, and a **Negative Correlation** means worse grades.")
    
    tab1, tab2, tab3 = st.tabs(["A. By Specific Tool", "B. By Mode of Use", "C. By Perception"])
    
    # --- TAB 1: TOOLS CORRELATION (ToolsAI.ipynb) ---
    with tab1:
        st.subheader("Correlation: Specific Tools vs. Grades")
        tool_cols = ['AI CHATBOT', 'AI FOR PROGRAMMING', 'WRITING ASSISTANT']
        
        if all(c in df.columns for c in tool_cols) and 'Performance_Target' in df.columns:
            correlations = df[tool_cols].corrwith(df['Performance_Target'])
            corr_df = pd.DataFrame({'AI Tool': correlations.index, 'Correlation': correlations.values})
            
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.lineplot(data=corr_df, x='AI Tool', y='Correlation', marker='o', markersize=10, linewidth=3, color='#1f77b4', ax=ax)
            ax.axhline(0, color='black', linewidth=1.5, linestyle='--')
            
            # Labels
            for i, val in enumerate(corr_df['Correlation']):
                offset = 0.005 if val >= 0 else -0.015
                ax.text(i, val + offset, f"{val:.4f}", ha='center', fontweight='bold')
            
            ax.set_ylim(min(corr_df['Correlation']) - 0.05, max(corr_df['Correlation']) + 0.05)
            st.pyplot(fig)
            
            st.markdown("""
            **Insights (from ToolsAI.ipynb):**
            * **The "Checkmark" Pattern:** * **Chatbots:** Neutral (No impact).
                * **Programming AI:** Negative trend (Risk of reliance).
                * **Writing Assistant:** Positive trend (Polishes work).
            """)

    # --- TAB 2: MODE CORRELATION (UseAI.ipynb) ---
    with tab2:
        st.subheader("Correlation: Modes of Use vs. Grades")
        mode_cols = ['Coding', 'Academic Assignment', 'Learning Support', 'Research']
        
        if all(c in df.columns for c in mode_cols) and 'Performance_Target' in df.columns:
            correlations = df[mode_cols].corrwith(df['Performance_Target'])
            corr_df = pd.DataFrame({'Mode of Use': correlations.index, 'Correlation': correlations.values})
            corr_df = corr_df.sort_values(by='Correlation', ascending=False)
            
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.lineplot(data=corr_df, x='Mode of Use', y='Correlation', marker='o', markersize=10, linewidth=3, color='#1f77b4', ax=ax)
            ax.axhline(0, color='black', linewidth=1.5, linestyle='--')
            
            # Labels
            for i, val in enumerate(corr_df['Correlation']):
                offset = 0.005 if val >= 0 else -0.015
                ax.text(i, val + offset, f"{val:.4f}", ha='center', fontweight='bold')

            ax.set_ylim(min(corr_df['Correlation']) - 0.05, max(corr_df['Correlation']) + 0.05)
            st.pyplot(fig)
            
            st.markdown("""
            **Insights (from UseAI.ipynb):**
            * **Coding is the Outlier:** Using AI to *actively* code/debug is the only mode with a strong positive link to grades.
            * **Research is Negative:** Passive searching via AI correlates with slightly lower performance.
            """)

    # --- TAB 3: PREDICTIVE/PERCEPTION (obj5.ipynb) ---
    with tab3:
        st.subheader("Correlation: Perception & Mindset vs. Grades")
        predictors = [
            'General Perception of AI in Higher Education',
            'Current use of AI in Higher Education ',
            'Impact of AI on the Students Experience ',
            'Concern about the use of AI in higher education',
            'Future expectations of AI in higher education '
        ]
        valid_predictors = [c for c in predictors if c in df.columns]
        
        if valid_predictors and 'Performance_Target' in df.columns:
            correlations = df[valid_predictors].corrwith(df['Performance_Target']).sort_values(ascending=False)
            
            fig, ax = plt.subplots(figsize=(10, 6))
            colors = ['#1f77b4' if x >= 0 else '#d62728' for x in correlations.values]
            sns.barplot(x=correlations.values, y=correlations.index, palette=colors, ax=ax)
            ax.axvline(0, color='black', linewidth=1)
            
            # Labels
            for i, v in enumerate(correlations.values):
                offset = 0.005 if v >= 0 else -0.005
                ha_align = 'left' if v >= 0 else 'right'
                ax.text(v + offset, i, f"{v:.4f}", va='center', ha=ha_align, fontweight='bold', color='black')
                
            st.pyplot(fig)
            
            st.markdown("""
            **Insights (from obj5.ipynb):**
            * **Current Use Intensity:** The strongest predictor. Active users perform better.
            * **Optimism:** Future expectations and positive perception align with success.
            * **Concern:** Even students concerned about AI risks perform well, suggesting they are "critical users."
            """)