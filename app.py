import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================
st.set_page_config(page_title="AI Usage & Academic Performance", layout="wide")

st.title("📊 Navigating Learning: AI Usage & Academic Performance")
st.markdown("### Interactive Analysis Dashboard")

# ==========================================
# 2. DATA LOADING
# ==========================================
@st.cache_data
def load_data():
    file_path = "dataset.xlsx"
    try:
        df = pd.read_excel(file_path, engine='openpyxl')
    except Exception:
        return None

    # --- PREPROCESSING ---
    grade_col = "Current Year Average Grade:"
    if grade_col in df.columns:
        df[grade_col] = pd.to_numeric(df[grade_col], errors='coerce')
        df['Performance_Target'] = df[grade_col] * -1
        
        def categorize_grade(grade):
            if pd.isna(grade): return "Unknown"
            elif grade <= 1.25: return "Excellent"
            elif grade <= 1.75: return "Very Good"
            elif grade <= 2.25: return "Good"
            elif grade <= 2.75: return "Fair"
            elif grade <= 3.00: return "Pass"
            else: return "Fail"
        df['Grade_Description'] = df[grade_col].apply(categorize_grade)

    # Tool & Mode columns cleaning
    cols_to_clean = ['AI CHATBOT', 'AI FOR PROGRAMMING', 'WRITING ASSISTANT', 
                     'Coding', 'Academic Assignment', 'Learning Support', 'Research']
    for col in cols_to_clean:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # Likert columns cleaning
    # Note: Trailing spaces are important if they exist in the Excel file
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

df = load_data()
if df is None:
    st.error("dataset.xlsx not found. Please ensure it is in the same folder.")
    st.stop()

# ==========================================
# 3. SIDEBAR NAVIGATION
# ==========================================
st.sidebar.header("Navigation")
page = st.sidebar.radio("Select Analysis Module:", 
    ["1. Overview (Grade Distribution)", 
     "2. AI Usage Habits (Tools & Modes)", 
     "3. Impact Analysis (Correlations)",
     "4. Respondents’ description of their AI usage (Tables)"]
)
st.sidebar.markdown("---")
st.sidebar.info(f"**Total Respondents:** {len(df)}")

# ==========================================
# PAGE 1: OVERVIEW
# ==========================================
if page == "1. Overview (Grade Distribution)":
    st.header("1. Overview of Academic Performance")
    if 'Grade_Description' in df.columns:
        grade_counts = df['Grade_Description'].value_counts()
        fig, ax = plt.subplots(figsize=(8, 8))
        colors = sns.color_palette('pastel')[0:len(grade_counts)]
        ax.pie(grade_counts, labels=grade_counts.index, autopct='%1.1f%%', 
               startangle=140, colors=colors, textprops={'fontsize': 12, 'fontweight': 'bold'})
        st.pyplot(fig)

# ==========================================
# PAGE 2: USAGE HABITS
# ==========================================
elif page == "2. AI Usage Habits (Tools & Modes)":
    st.header("2. AI Usage Habits")
    tab1, tab2 = st.tabs(["A. Types of Tools", "B. Mode of Use"])
    
    with tab1:
        st.subheader("Prevalence of AI Tools")
        tool_cols = ['AI CHATBOT', 'AI FOR PROGRAMMING', 'WRITING ASSISTANT']
        if all(c in df.columns for c in tool_cols):
            tool_counts = df[tool_cols].sum().sort_values(ascending=False)
            fig, ax = plt.subplots(figsize=(8, 5))
            sns.barplot(x=tool_counts.index, y=tool_counts.values, hue=tool_counts.index, palette='viridis', legend=False, ax=ax)
            for i, v in enumerate(tool_counts.values):
                ax.text(i, v + 0.5, str(int(v)), ha='center', fontweight='bold')
            st.pyplot(fig)

    with tab2:
        st.subheader("Primary Purpose of AI Usage")
        mode_cols = ['Coding', 'Academic Assignment', 'Learning Support', 'Research']
        if all(c in df.columns for c in mode_cols):
            counts_df = df[mode_cols].apply(pd.Series.value_counts).T
            if 0 not in counts_df.columns: counts_df[0] = 0
            if 1 not in counts_df.columns: counts_df[1] = 0
            counts_df.columns = ['No', 'Yes']
            counts_df = counts_df.sort_values(by='Yes', ascending=False)
            fig, ax = plt.subplots(figsize=(10, 6))
            counts_df.plot(kind='bar', stacked=True, color=['#ff9999', '#66b3ff'], ax=ax, width=0.7)
            ax.legend(title='Response', labels=['Non-User', 'User'])
            st.pyplot(fig)

# ==========================================
# PAGE 3: IMPACT ANALYSIS
# ==========================================
elif page == "3. Impact Analysis (Correlations)":
    st.header("3. Impact on Academic Performance")
    tab1, tab2 = st.tabs(["A. By Specific Tool", "B. By Mode of Use"])
    
    with tab1:
        st.subheader("Correlation: Specific Tools vs. Grades")
        tool_cols = ['AI CHATBOT', 'AI FOR PROGRAMMING', 'WRITING ASSISTANT']
        if all(c in df.columns for c in tool_cols) and 'Performance_Target' in df.columns:
            correlations = df[tool_cols].corrwith(df['Performance_Target'])
            corr_df = pd.DataFrame({'AI Tool': correlations.index, 'Correlation': correlations.values})
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.lineplot(data=corr_df, x='AI Tool', y='Correlation', marker='o', markersize=10, linewidth=3, color='#1f77b4', ax=ax)
            ax.axhline(0, color='black', linewidth=1.5, linestyle='--')
            for i, val in enumerate(corr_df['Correlation']):
                ax.text(i, val + 0.005, f"{val:.4f}", ha='center', fontweight='bold')
            st.pyplot(fig)

    with tab2:
        st.subheader("Correlation: Modes of Use vs. Grades")
        mode_cols = ['Coding', 'Academic Assignment', 'Learning Support', 'Research']
        if all(c in df.columns for c in mode_cols) and 'Performance_Target' in df.columns:
            correlations = df[mode_cols].corrwith(df['Performance_Target']).sort_values(ascending=False)
            corr_df = pd.DataFrame({'Mode of Use': correlations.index, 'Correlation': correlations.values})
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.lineplot(data=corr_df, x='Mode of Use', y='Correlation', marker='o', markersize=10, linewidth=3, color='#1f77b4', ax=ax)
            ax.axhline(0, color='black', linewidth=1.5, linestyle='--')
            for i, val in enumerate(corr_df['Correlation']):
                ax.text(i, val + 0.005, f"{val:.4f}", ha='center', fontweight='bold')
            st.pyplot(fig)

# ==========================================
# PAGE 4: RESPONDENTS' DESCRIPTION (TABLE IMAGES)
# ==========================================
elif page == "4. Respondents’ description of their AI usage (Tables)":
    st.header("4. Respondents’ description of their AI usage Analysis")
    st.markdown("Image of Data Tables.")

    # Helper function to display an image section
    def display_section(col_name, title, image_name):
        # Only display if the corresponding data column exists in the Excel file
        if col_name in df.columns:
            st.markdown("---")
            st.subheader(title)
            
            # Check if file exists automatically in the folder
            if os.path.exists(image_name):
                st.image(image_name, caption=title, use_container_width=True)
            else:
                # Fallback: Allow manual upload if file is missing
                uploaded = st.file_uploader(f"Upload {image_name}", type=['png', 'jpg', 'jpeg'], key=image_name)
                if uploaded:
                    st.image(uploaded, caption=title, use_container_width=True)
                else:
                    st.info(f"Save your image as '{image_name}' in the project folder to display it here automatically.")

    # --- TABLE 1 ---
    display_section(
        'General Perception of AI in Higher Education', 
        "Table 1: General Perception (GPI)", 
        "table1.png"
    )

    # --- TABLE 2 ---
    display_section(
        'Current use of AI in Higher Education ', 
        "Table 2: Current Use of AI (UAI)", 
        "table2.png"
    )

    # --- TABLE 3 ---
    display_section(
        'Impact of AI on the Students Experience ', 
        "Table 3: Impact on Student Experience (ISE)", 
        "table3.png"
    )

    # --- TABLE 4 (NEW) ---
    display_section(
        'Concern about the use of AI in higher education',
        "Table 4: Concerns About the Use of AI in Higher Education (CAU)",
        "table4.png"
    )

    # --- TABLE 5 (NEW) ---
    # Note: The trailing space in the column name is crucial based on your data
    display_section(
        'Future expectations of AI in higher education ',
        "Table 5: Future Expectations of AI in Higher Education (EAI)",
        "table5.png"
    )
