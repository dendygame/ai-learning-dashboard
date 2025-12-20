import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# Set page config
st.set_page_config(page_title="AI Usage & Academic Outcomes Dashboard", layout="wide")

# --- TITLE ---
st.title("Data Analysis Dashboard: Navigating Learning with AI: Usage Patterns and Academic Outcomes of IT Students of NEUST Talavera Off-Campus")
st.markdown("Analyze correlation trends, mean values, and custom relationships.")

# --- HELPER: Categorize Grades ---
def categorize_grade(grade):
    if pd.isna(grade): return "Unknown"
    elif grade <= 1.25: return "Excellent"
    elif grade <= 1.75: return "Very Good"
    elif grade <= 2.25: return "Good"
    elif grade <= 2.75: return "Average"
    elif grade <= 3.00: return "Satistfactory"
    else: return "Fail"

# --- HELPER: Likert Mapping ---
likert_mapping = {
    1: "Strongly Disagree",
    2: "Disagree",
    3: "Neutral",
    4: "Agree",
    5: "Strongly Agree"
}
# Logical order for sorting legends (not data values)
likert_order = ["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"]
grade_order = ["Excellent", "Very Good", "Good", "Average", "Satistfactory", "Fail", "Unknown"]

# --- DATA LOADER ---
@st.cache_data
def load_data():
    possible_filenames = ["dataset.csv", "dataset.xlsx"]
    for filename in possible_filenames:
        if os.path.exists(filename):
            try:
                if filename.endswith(".csv"):
                    return pd.read_csv(filename)
                elif filename.endswith(".xlsx"):
                    return pd.read_excel(filename)
            except Exception as e:
                st.error(f"Found {filename} but couldn't read it: {e}")
    return None

df = load_data()

# File Uploader Backup
if df is None:
    st.warning("⚠️ Could not find 'dataset.csv' or 'dataset.xlsx'. Please upload a file.")
    uploaded_file = st.file_uploader("Upload your dataset here", type=["csv", "xlsx"])
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith(".xlsx"):
                df = pd.read_excel(uploaded_file)
        except Exception as e:
            st.error(f"Error reading uploaded file: {e}")

# --- MAIN DASHBOARD ---
if df is not None:
    # 0. Safety: Remove Duplicate Columns
    df = df.loc[:, ~df.columns.duplicated()]

    # --- RENAME COLUMNS (ALL SECTIONS) ---
    rename_map = {
        # --- GPI SECTION ---
        "I believe AI has great potential to improve the\nquality of higher education for students.": "GPI Question #1",
        "I believe AI has great potential to improve the quality of higher education for students.": "GPI Question #1",
        "I think AI can positively transform the way students\nlearn and study.": "GPI Question #2",
        "I think AI can positively transform the way students learn and study.": "GPI Question #2",
        "AI can personalize my learning experiences\naccording to my needs.": "GPI Question #3",
        "AI can personalize my learning experiences according to my needs.": "GPI Question #3",
        "I am aware of AI applications being implemented\nin my educational institution.": "GPI Question #4",
        "I am aware of AI applications being implemented in my educational institution.": "GPI Question #4",
        "I have experienced benefits in my learning due to\nthe use of AI tools.": "GPI Question #5",
        "I have experienced benefits in my learning due to the use of AI tools.": "GPI Question #5",

        # --- UAI SECTION ---
        "I use AI systems (e.g., learning platforms, chatbots) to support\nmy studies.": "UAI Question #1",
        "I use AI systems (e.g., learning platforms, chatbots) to support my studies.": "UAI Question #1",
        "I have used online learning platforms that apply AI to assess\nmy progress and adapt content.": "UAI Question #2",
        "I have used online learning platforms that apply AI to assess my progress and adapt content.": "UAI Question #2",
        "I interact with AI chatbots or virtual assistants to get academic\nhelp.": "UAI Question #3",
        "I interact with AI chatbots or virtual assistants to get academic help.": "UAI Question #3",
        "I use AI tools in research, data analysis, or coding tasks for my\ncourses.": "UAI Question #4",
        "I use AI tools in research, data analysis, or coding tasks for my courses.": "UAI Question #4",
        "In my experience, AI has had a positive impact on my learning\nand academic performance.": "UAI Question #5",
        "In my experience, AI has had a positive impact on my learning and academic performance.": "UAI Question #5",

        # --- ISE SECTION ---
        "AI helps personalize learning content according to my needs\nand preferences.": "ISE Question #1",
        "AI helps personalize learning content according to my needs and preferences.": "ISE Question #1",
        "AI makes learning resources more accessible for me and my\npeers.": "ISE Question #2",
        "AI makes learning resources more accessible for me and my peers.": "ISE Question #2",
        "AI improves my ability to keep up with online or hybrid\nclasses.": "ISE Question #3",
        "AI improves my ability to keep up with online or hybrid classes.": "ISE Question #3",
        "AI influences how academic tasks and assignments are\nmanaged in my courses.": "ISE Question #4",
        "AI influences how academic tasks and assignments are managed in my courses.": "ISE Question #4",
        "AI enhances interaction and communication with my\nclassmates and instructors.": "ISE Question #5",
        "AI enhances interaction and communication with my classmates and instructors.": "ISE Question #5",

        # --- CAU SECTION ---
        "I am concerned about the privacy of my personal data when AI\nsystems are used.": "CAU Question #1",
        "I am concerned about the privacy of my personal data when AI systems are used.": "CAU Question #1",
        "I am concerned that AI could create inequality in access to\neducational resources.": "CAU Question #2",
        "I am concerned that AI could create inequality in access to educational resources.": "CAU Question #2",
        "I worry that AI could replace some teaching or learning roles in the\nfuture.": "CAU Question #3",
        "I worry that AI could replace some teaching or learning roles in the future.": "CAU Question #3",
        "I am concerned about ethical issues in the use of AI algorithms in\neducation.": "CAU Question #4",
        "I am concerned about ethical issues in the use of AI algorithms in education.": "CAU Question #4",
        "I feel well-informed about institutional policies and practices\nregarding AI usage.": "CAU Question #5",
        "I feel well-informed about institutional policies and practices regarding AI usage.": "CAU Question #5",

        # --- EAI SECTION ---
        "I believe AI will play a more significant role in higher\neducation in the future.": "EAI Question #1",
        "I believe AI will play a more significant role in higher education in the future.": "EAI Question #1",
        "I hope that AI will enhance the quality of learning in the\ncoming years.": "EAI Question #2",
        "I hope that AI will enhance the quality of learning in the coming years.": "EAI Question #2",
        "I expect AI to make higher education more accessible for\nstudents.": "EAI Question #3",
        "I expect AI to make higher education more accessible for students.": "EAI Question #3",
        "I believe AI will be essential in online learning and education\nin the future.": "EAI Question #4",
        "I believe AI will be essential in online learning and education in the future.": "EAI Question #4",
        "I think specific areas of my courses or field of study will\nbenefit from AI development.": "EAI Question #5",
        "I think specific areas of my courses or field of study will benefit from AI development.": "EAI Question #5"
    }
    df.rename(columns=rename_map, inplace=True)

    # 1. Clean Grade Column
    grade_col_name = "Current Year Average Grade:"
    if grade_col_name not in df.columns:
        possible = [c for c in df.columns if "Grade" in c]
        if possible: grade_col_name = possible[0]
        
    if grade_col_name in df.columns:
        df[grade_col_name] = pd.to_numeric(df[grade_col_name], errors='coerce')
        df['Grade Category'] = df[grade_col_name].apply(categorize_grade)

    # 2. Clean Tool Columns
    tool_cols = ['AI CHATBOT', 'AI FOR PROGRAMMING', 'WRITING ASSISTANT']
    for col in tool_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
    # 3. Clean Purpose Columns
    mode_cols = ['Coding', 'Academic Assignment', 'Learning Support', 'Research']
    for col in mode_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # 4. Create Respondent ID Column if not exists
    if 'Respondent ID' not in df.columns:
        df.insert(0, 'Respondent ID', range(1, len(df) + 1))
    
    # --- SIDEBAR SETTINGS ---
    st.sidebar.header("Settings")
    
    # --- SHOW DATASET TOGGLE ---
    show_raw_data = st.sidebar.checkbox("Show Raw Dataset", value=False)

    numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
    all_cols = df.columns.tolist()
    
    # A. Target Variable (Global)
    default_target_ix = 0
    if grade_col_name in numeric_cols:
        default_target_ix = numeric_cols.index(grade_col_name)
    elif grade_col_name in all_cols:
        default_target_ix = all_cols.index(grade_col_name)
    
    target_var = st.sidebar.selectbox(
        "Select Target Variable (e.g., Grade):",
        options=all_cols, 
        index=default_target_ix
    )

    # B. Attributes to Compare (Global)
    available_attributes = [c for c in all_cols if c != "Respondent ID" and c != target_var]
    
    # --- NO DEFAULT SELECTION ---
    compared_attributes = st.sidebar.multiselect(
        "Select Attributes to Compare:",
        options=available_attributes,
        default=[] 
    )

    # --- DISPLAY RAW DATA IF CHECKED ---
    if show_raw_data:
        st.subheader("Raw Dataset Preview")
        st.markdown(f"**Shape:** {df.shape[0]} rows × {df.shape[1]} columns")
        st.dataframe(df, use_container_width=True)
        st.divider()

    # --- CALCULATION LOGIC (Global) ---
    if target_var and compared_attributes:
        # Pre-process for Sidebar logic
        df[target_var] = pd.to_numeric(df[target_var], errors='coerce')
        for col in compared_attributes:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        # Correlation Calculation
        global_corrs = df[compared_attributes].corrwith(df[target_var])
        is_grade_target = (target_var == grade_col_name)
        if is_grade_target:
            global_corrs = global_corrs * -1
        global_corr_df = pd.DataFrame({'Attribute': global_corrs.index, 'Correlation': global_corrs.values})
        
        # --- COMPREHENSIVE STATISTICS CALCULATION ---
        stats_df = df[compared_attributes].agg(['mean', 'median', 'std', 'var', 'min', 'max', 'skew', 'kurt'])
        modes = df[compared_attributes].mode().iloc[0]
        stats_df.loc['mode'] = modes
        
        summary_df = stats_df.T
        summary_df.columns = ['Mean', 'Median', 'Std Dev', 'Variance', 'Min', 'Max', 'Skewness', 'Kurtosis', 'Mode']
        summary_df = summary_df[['Mean', 'Median', 'Mode', 'Std Dev', 'Variance', 'Min', 'Max', 'Skewness', 'Kurtosis']]

        # --- SECTION 1: COMPUTED STATISTICS ---
        st.header("1. Computed Statistics")
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Descriptive Statistics")
            st.dataframe(summary_df, use_container_width=True)
            
        with col2:
            st.subheader(f"Correlation with {target_var}")
            display_corr = global_corr_df.set_index('Attribute')
            st.dataframe(display_corr, use_container_width=True)

        # --- SECTION 2: VISUALIZATIONS ---
        st.header("2. Visualizations")
        
        graph_type = st.selectbox(
            "Select Graph Type:",
            [
                "Scatter Plot",
                "Line Graph",
                "Area Chart",
                "Bar Graph (Vertical)",
                "Bar Graph (Horizontal)",
                "Stacked Bar Graph (Custom)",
                "Grouped Bar Graph",
                "Pie Chart",
                "Donut Chart",
                "Histogram",
                "Box Plot",
                "Violin Plot",
                "Strip Plot",
                "Funnel Chart",
                "Density Heatmap"
            ]
        )

        st.subheader("Plot Configuration")
        
        # --- DATA MODE SELECTOR ---
        data_mode = st.radio(
            "Data Representation Mode:", 
            ["Raw Data (Individual)", "Count (Frequency)", "Likert Scale Distribution", "Mean Value (Flexible)", "Trend of Correlation Coefficient"], 
            horizontal=True
        )

        # --- NEW GLOBAL SORTING ORDER ---
        sort_order = st.radio(
            "Sort Data Order:",
            ["None (Default)", "Ascending (Low to High)", "Descending (High to Low)"],
            horizontal=True
        )

        # --- PRE-PLOT CALCULATION BLOCKS ---
        plot_df = pd.DataFrame()
        local_corr_df = pd.DataFrame()
        agg_df = pd.DataFrame()
        
        # Shared Color Settings Holders
        selected_scale = None
        custom_color = None
        discrete_seq = None
        likert_color_mode = None
        likert_xaxis_var = "Question"
        likert_color_var = "Response"

        # A. SETUP FOR CORRELATION
        if data_mode == "Trend of Correlation Coefficient":
            with st.expander("Step 1: Correlation Settings (Input Data)", expanded=True):
                c_input1, c_input2 = st.columns(2)
                with c_input1:
                    # Select Target
                    corr_target_var = st.selectbox(
                        "Select Target Variable:",
                        options=numeric_cols,
                        index=numeric_cols.index(grade_col_name) if grade_col_name in numeric_cols else 0
                    )
                with c_input2:
                    # Select Attributes
                    corr_attr_vars = st.multiselect(
                        "Select Attributes to Correlate:",
                        options=[c for c in numeric_cols if c != corr_target_var],
                        default=[c for c in numeric_cols if c != corr_target_var][:5]
                    )
                
            if corr_target_var and corr_attr_vars:
                target_series = pd.to_numeric(df[corr_target_var], errors='coerce')
                attr_df = df[corr_attr_vars].apply(pd.to_numeric, errors='coerce').fillna(0)
                local_corr = attr_df.corrwith(target_series)
                
                if "Grade" in corr_target_var:
                    local_corr = local_corr * -1
                    st.caption("ℹ️ Note: Correlation flipped (-1) assuming lower Grade = better performance.")
                    
                local_corr_df = pd.DataFrame({'Attribute': local_corr.index, 'Correlation': local_corr.values})
                plot_df = local_corr_df # Assign to main plotter df

        # B. SETUP FOR LIKERT
        elif data_mode == "Likert Scale Distribution":
            st.info("Visualizes the distribution of responses (1-5 scale) or Grades.")
            
            # 1. Dimensions
            st.markdown("**1. Dimensions**")
            c_dim1, c_dim2 = st.columns(2)
            with c_dim1:
                likert_xaxis_var = st.selectbox("Group X-Axis By:", ["Question", "Grade Category", "Response"], index=0)
            with c_dim2:
                likert_color_var = st.selectbox("Color Stack By:", ["Response", "Grade Category", "Question"], index=0)

            # 2. Select Questions
            possible_likert = [c for c in numeric_cols if df[c].nunique() < 15]
            if not possible_likert: possible_likert = numeric_cols[:5]
            
            likert_cols = []
            if likert_xaxis_var == "Grade Category":
                st.caption("ℹ️ **Optional:** Select questions to break down responses by grade. Leave empty to see Grade Counts only.")
                likert_cols = st.multiselect("Select Likert Questions (Optional):", options=[c for c in all_cols if c not in ["Respondent ID", target_var]], default=[])
            else:
                likert_cols = st.multiselect("Select Likert Questions:", options=[c for c in all_cols if c not in ["Respondent ID", target_var]], default=possible_likert[:5])
            
            # 3. Categorization Logic
            st.markdown("---")
            col_lik_1, col_lik_2 = st.columns(2)
            with col_lik_1:
                # --- UPDATED RESPONSE LABELS ---
                likert_label_mode = st.radio(
                    "Response Labels:", 
                    ["Likert 5-Point (Strongly Disagree...)", "Binary (No / Yes)", "Binary (Yes Only)", "Binary (No Only)", "Numeric Values"]
                )
            with col_lik_2:
                likert_val_type = st.selectbox("Value Type:", ["Count", "Percentage"])

            # 4. Color Logic
            st.markdown("---")
            st.markdown("**Color & Style Settings**")
            c_mode, c_picker = st.columns([1, 1])
            with c_mode:
                likert_color_mode = st.selectbox("Color Logic:", ["By Legend (Categories)", "By Count (Scale)", "Single Color"])
            
            with c_picker:
                if likert_color_mode == "By Legend (Categories)":
                    qual_opts = ["Plotly", "D3", "G10", "T10", "Alphabet", "Dark24", "Light24", "Pastel", "Bold"]
                    sel_qual = st.selectbox("Theme:", qual_opts, index=0)
                    discrete_seq = getattr(px.colors.qualitative, sel_qual)
                elif likert_color_mode == "By Count (Scale)":
                    scale_opts = ["Viridis", "Plasma", "Inferno", "Magma", "Cividis", "Blues", "Reds", "Greens"]
                    selected_scale = st.selectbox("Palette:", scale_opts, index=5)
                else:
                    custom_color = st.color_picker("Pick Color:", "#1f77b4")

            # --- PROCESSING LOGIC ---
            if likert_cols:
                subset = df[likert_cols].copy()
                if 'Grade Category' in df.columns:
                    subset['Grade Category'] = df['Grade Category']
                else:
                    subset['Grade Category'] = "Unknown"

                melted = subset.melt(id_vars=['Grade Category'], var_name="Question", value_name="Response")
                
                # MAPPING LOGIC
                if likert_label_mode == "Likert 5-Point (Strongly Disagree...)":
                    melted["Response"] = pd.to_numeric(melted["Response"], errors='coerce').map(likert_mapping).fillna("Unknown")
                    melted["Response"] = pd.Categorical(melted["Response"], categories=likert_order + ["Unknown"], ordered=True)
                
                elif "Binary" in likert_label_mode: # Handles No/Yes, Yes Only, No Only
                    binary_map = {0: "No", 1: "Yes"}
                    melted["Response"] = pd.to_numeric(melted["Response"], errors='coerce').map(binary_map).fillna("Unknown")
                    
                    # --- FILTERING LOGIC ---
                    if likert_label_mode == "Binary (Yes Only)":
                        melted = melted[melted["Response"] == "Yes"]
                    elif likert_label_mode == "Binary (No Only)":
                        melted = melted[melted["Response"] == "No"]
                        
                    melted["Response"] = pd.Categorical(melted["Response"], categories=["No", "Yes", "Unknown"], ordered=True)
                
                if 'Grade Category' in melted.columns:
                    melted["Grade Category"] = pd.Categorical(melted["Grade Category"], categories=grade_order, ordered=True)

                grp_cols = [likert_xaxis_var, likert_color_var]
                grp_cols = list(dict.fromkeys(grp_cols)) # Dedup
                
                plot_df = melted.groupby(grp_cols, observed=True).size().reset_index(name="Count")
                plot_df = plot_df[plot_df["Count"] > 0] 
                
                if likert_val_type == "Percentage":
                    totals = plot_df.groupby(likert_xaxis_var, observed=True)["Count"].transform("sum")
                    plot_df["Percentage"] = (plot_df["Count"] / totals) * 100
                
                for col in plot_df.select_dtypes(include=['category']).columns:
                    plot_df[col] = plot_df[col].cat.remove_unused_categories()

            elif likert_xaxis_var == "Grade Category" and not likert_cols:
                if 'Grade Category' in df.columns:
                    plot_df = df['Grade Category'].value_counts().reset_index()
                    plot_df.columns = ['Grade Category', 'Count']
                    plot_df['Grade Category'] = pd.Categorical(plot_df['Grade Category'], categories=grade_order, ordered=True)
                    
                    if likert_val_type == "Percentage":
                        total = plot_df['Count'].sum()
                        plot_df['Percentage'] = (plot_df['Count'] / total) * 100

                    plot_df = plot_df[plot_df['Count'] > 0]
                    plot_df['Grade Category'] = plot_df['Grade Category'].cat.remove_unused_categories()
                    
                    if likert_color_var not in plot_df.columns:
                        likert_color_var = "Grade Category" 
                        if likert_color_mode == "By Legend (Categories)":
                            color_enc = "Grade Category"
                else:
                    st.warning("No Grade Category column found.")

        # C. SETUP FOR MEAN VALUE
        elif data_mode == "Mean Value (Flexible)":
            st.info("ℹ️ Step 1: Select Variables. Leave 'Grouping' EMPTY to compare multiple variables globally.")
            row_agg = st.columns(2)
            with row_agg[0]:
                group_cols = st.multiselect("Grouping Categories (Optional):", options=[c for c in all_cols if c != "Respondent ID"])
            with row_agg[1]:
                metric_cols = st.multiselect("Numerical Variables:", options=numeric_cols)
            
            if metric_cols:
                try:
                    if group_cols:
                        count_df = df.groupby(group_cols).size().reset_index(name="Count")
                        mean_df = df.groupby(group_cols)[metric_cols].mean().add_prefix("Mean ").reset_index()
                        median_df = df.groupby(group_cols)[metric_cols].median().add_prefix("Median ").reset_index()
                        agg_df = pd.merge(count_df, mean_df, on=group_cols)
                        agg_df = pd.merge(agg_df, median_df, on=group_cols)
                    else:
                        means = df[metric_cols].mean()
                        medians = df[metric_cols].median()
                        agg_df = pd.DataFrame({
                            "Metric Name": metric_cols,
                            "Mean Value": means.values,
                            "Median Value": medians.values
                        })
                except Exception as e:
                    st.error(f"Aggregation Error: {e}")
            plot_df = agg_df

        # D. SETUP FOR OTHERS
        else:
            plot_df = df.copy()

        # --- PLOTTING CONFIGURATION (Axes) ---
        if data_mode != "Likert Scale Distribution": 
            st.divider()
        
        c1, c2, c3, c4 = st.columns(4)
        
        # Initialize holders
        x_cols = []
        y_cols = []
        color_enc = None
        
        # 1. X-AXIS SELECTION
        with c1:
            if data_mode == "Likert Scale Distribution":
                x_axis = likert_xaxis_var
            elif data_mode == "Trend of Correlation Coefficient":
                st.markdown("**X-Axis:**")
                x_cols = st.selectbox("Select X Dimension:", options=["Attribute", "Correlation"], index=0) 
                x_axis = x_cols
            elif data_mode == "Count (Frequency)":
                x_cols = st.multiselect("Category to Count (X-axis):", options=all_cols, default=[all_cols[0]] if all_cols else None)
            elif data_mode == "Mean Value (Flexible)":
                if not agg_df.empty:
                    def_x = [group_cols[0]] if group_cols else ["Metric Name"]
                    x_cols = st.multiselect("X-Axis:", options=agg_df.columns, default=def_x)
                else:
                    st.warning("Select Metrics first.")
            else:
                def_x = [all_cols[1]] if len(all_cols) > 1 else [all_cols[0]]
                x_cols = st.multiselect("X-axis:", options=all_cols, default=def_x)
        
        # 2. Y-AXIS SELECTION
        with c2:
            if data_mode == "Likert Scale Distribution":
                if likert_val_type == "Percentage" and "Percentage" in plot_df.columns:
                    y_axis = "Percentage"
                else:
                    y_axis = "Count"
            elif data_mode == "Trend of Correlation Coefficient":
                st.markdown("**Y-Axis:**")
                y_cols = st.selectbox("Select Y Dimension:", options=["Attribute", "Correlation"], index=1)
                y_axis = y_cols
            elif data_mode == "Count (Frequency)":
                st.info("Y-axis: Count (Auto)")
                y_axis = "Count"
            elif data_mode == "Mean Value (Flexible)":
                if not agg_df.empty:
                        y_cols = st.multiselect("Y-Axis:", options=agg_df.columns, default=["Mean Value"] if "Mean Value" in agg_df.columns else None)
            elif graph_type == "Histogram":
                y_axis = None
            elif "Pie" in graph_type or "Donut" in graph_type:
                y_opts = ["Count"] + [c for c in numeric_cols if c != "Respondent ID"]
                y_val = st.selectbox("Values:", options=y_opts)
                y_axis = None if y_val == "Count" else y_val
            elif graph_type == "Density Heatmap":
                y_cols = st.multiselect("Y-axis:", options=all_cols, default=[all_cols[1]] if len(all_cols)>1 else [all_cols[0]])
            else:
                y_raw_opts = ["Count"] + [c for c in numeric_cols if c != "Respondent ID"]
                y_cols = st.multiselect("Y-axis:", options=y_raw_opts, default=["Count"])
        
        # 3. COLOR SELECTION
        with c3:
            if data_mode == "Likert Scale Distribution":
                if likert_xaxis_var == "Grade Category" and not likert_cols:
                    color_enc = "Grade Category"
                else:
                    color_enc = likert_color_var
            elif data_mode == "Trend of Correlation Coefficient":
                color_enc = st.selectbox("Color By:", options=[None, "Attribute", "Correlation"], index=2)
            elif data_mode == "Mean Value (Flexible)":
                if not agg_df.empty:
                    color_enc = st.selectbox("Color By:", options=[None] + agg_df.columns.tolist(), index=0)
                else:
                    color_enc = None
            else:
                color_enc = st.selectbox("Color By (Legend):", options=[None] + all_cols)
        
        # 4. PALETTE SELECTION
        with c4:
            if data_mode != "Likert Scale Distribution":
                use_scale = False
                
                if data_mode == "Trend of Correlation Coefficient" and color_enc == "Correlation":
                    use_scale = True
                elif data_mode == "Mean Value (Flexible)" and color_enc and not agg_df.empty:
                    if pd.api.types.is_numeric_dtype(agg_df[color_enc]):
                        use_scale = True
                elif color_enc and data_mode not in ["Likert Scale Distribution", "Mean Value (Flexible)", "Trend of Correlation Coefficient"]:
                    if color_enc in df.columns and pd.api.types.is_numeric_dtype(df[color_enc]) and len(df[color_enc].unique()) > 10:
                        use_scale = True
                
                if use_scale:
                    scale_opts = ["Viridis", "Plasma", "Inferno", "Magma", "Cividis", "Blues", "Reds", "Greens"]
                    selected_scale = st.selectbox("Color Scale:", scale_opts, index=0)
                elif color_enc:
                    qual_opts = ["Plotly", "D3", "G10", "T10", "Alphabet", "Dark24", "Light24", "Pastel", "Bold"]
                    sel_qual = st.selectbox("Legend Theme:", qual_opts, index=0)
                    discrete_seq = getattr(px.colors.qualitative, sel_qual)
                else:
                    custom_color = st.color_picker("Pick Color:", "#1f77b4")

        # --- PLOT GENERATION ---
        generation_success = True
        error_message = ""

        try:
            # Count Logic
            if data_mode == "Count (Frequency)":
                if not x_cols: raise ValueError("Select X-axis.")
                groups = x_cols.copy()
                if color_enc and color_enc not in groups: groups.append(color_enc)
                plot_df = df.groupby(groups).size().reset_index(name='Count')
                x_axis = x_cols

            # Raw Logic
            elif data_mode == "Raw Data (Individual)":
                if len(y_cols) == 1 and y_cols[0] == "Count":
                    groups = x_cols.copy() if isinstance(x_cols, list) else [x_cols]
                    if color_enc and color_enc not in groups: groups.append(color_enc)
                    plot_df = df.groupby(groups).size().reset_index(name='Count')
                    y_axis = "Count"
                else:
                    y_axis = y_cols
                x_axis = x_cols
            
            # Correlation / Aggregate / Likert already have plot_df ready
            elif data_mode == "Trend of Correlation Coefficient":
                if plot_df.empty: raise ValueError("Please select a Target and Attributes in Step 1.")
            elif data_mode == "Mean Value (Flexible)":
                x_axis = x_cols
                y_axis = y_cols

        except Exception as e:
            generation_success = False
            error_message = str(e)

        # RENDER
        if generation_success and not plot_df.empty:
            try:
                final_x = x_axis[0] if isinstance(x_axis, list) and len(x_axis)==1 else x_axis
                final_y = y_axis[0] if isinstance(y_axis, list) and len(y_axis)==1 else y_axis
                
                # --- UNIVERSAL SORTING LOGIC ---
                if sort_order != "None (Default)":
                    is_asc = (sort_order == "Ascending (Low to High)")
                    
                    if data_mode == "Trend of Correlation Coefficient":
                        plot_df = plot_df.sort_values(by="Correlation", ascending=is_asc)
                        
                    elif data_mode == "Count (Frequency)":
                        plot_df = plot_df.sort_values(by="Count", ascending=is_asc)
                        
                    elif data_mode == "Likert Scale Distribution":
                        # For Likert, we sort by the total count/percentage per X-group
                        sort_metric = "Percentage" if "Percentage" in plot_df.columns else "Count"
                        
                        # 1. Calculate totals per X-axis group
                        totals = plot_df.groupby(likert_xaxis_var)[sort_metric].sum().reset_index()
                        totals = totals.sort_values(by=sort_metric, ascending=is_asc)
                        
                        # 2. Reorder the Categorical Type of the X-axis column
                        sorted_cats = totals[likert_xaxis_var].tolist()
                        plot_df[likert_xaxis_var] = pd.Categorical(plot_df[likert_xaxis_var], categories=sorted_cats, ordered=True)
                        plot_df = plot_df.sort_values(likert_xaxis_var)

                    elif data_mode == "Mean Value (Flexible)":
                        # Sort by the first metric selected in Y-axis
                        if final_y:
                            sort_col = final_y if isinstance(final_y, str) else final_y[0]
                            if sort_col in plot_df.columns:
                                plot_df = plot_df.sort_values(by=sort_col, ascending=is_asc)
                                
                    elif data_mode == "Raw Data (Individual)":
                        # Sort by Y-axis value if possible
                        if final_y:
                            sort_col = final_y if isinstance(final_y, str) else final_y[0]
                            if sort_col in plot_df.columns:
                                plot_df = plot_df.sort_values(by=sort_col, ascending=is_asc)
                # -------------------------------

                if "Pie" in graph_type or "Donut" in graph_type:
                    if isinstance(final_x, list): final_x = final_x[0]
                    if isinstance(final_y, list): final_y = final_y[0]

                plot_args = { "data_frame": plot_df, "x": final_x, "color": color_enc }
                
                if final_y and graph_type not in ["Pie Chart", "Donut Chart", "Histogram", "Density Heatmap"]:
                    plot_args["y"] = final_y
                if graph_type == "Density Heatmap":
                    plot_args["y"] = final_y
                
                # Labels and Text
                if data_mode == "Trend of Correlation Coefficient":
                    plot_df['Label'] = plot_df['Correlation'].apply(lambda x: f"{x:.4f}")
                    plot_args["text"] = 'Label'
                elif final_y and graph_type in ["Scatter Plot", "Line Graph", "Area Chart"] and not isinstance(final_y, list):
                    plot_args["text"] = final_y

                # --- COLOR APPLICATION ---
                if data_mode == "Likert Scale Distribution":
                    if likert_color_mode == "By Legend (Categories)":
                        plot_args["color_discrete_sequence"] = discrete_seq
                    elif likert_color_mode == "By Count (Scale)":
                        plot_args["color_continuous_scale"] = selected_scale
                        plot_args["color"] = "Count" 
                    else:
                        plot_args["color_discrete_sequence"] = [custom_color]
                        plot_args["color"] = None
                
                elif use_scale: plot_args["color_continuous_scale"] = selected_scale
                elif color_enc: plot_args["color_discrete_sequence"] = discrete_seq
                else: plot_args["color_discrete_sequence"] = [custom_color]

                fig = None
                
                # Standard Plot Types
                if graph_type == "Scatter Plot":
                    fig = px.scatter(**plot_args)
                    if data_mode != "Trend of Correlation Coefficient": fig.update_traces(textposition='top center')
                elif graph_type == "Line Graph":
                    fig = px.line(**plot_args)
                    if data_mode == "Trend of Correlation Coefficient":
                        fig.update_traces(textposition='top center', mode='lines+markers+text')
                    elif not isinstance(final_y, list): 
                        fig.update_traces(textposition='top center')
                elif graph_type == "Area Chart":
                    fig = px.area(**plot_args)
                    if data_mode == "Trend of Correlation Coefficient":
                        fig.update_traces(textposition='top center', mode='lines+markers+text')
                elif graph_type == "Bar Graph (Vertical)":
                    fig = px.bar(**plot_args, text_auto=(data_mode != "Trend of Correlation Coefficient"))
                    if data_mode == "Trend of Correlation Coefficient": fig.update_traces(textposition='auto')
                elif graph_type == "Bar Graph (Horizontal)":
                    fig = px.bar(**plot_args, orientation='h', text_auto=(data_mode != "Trend of Correlation Coefficient"))
                    if data_mode == "Trend of Correlation Coefficient": fig.update_traces(textposition='auto')
                
                # Complex Types
                elif graph_type == "Stacked Bar Graph (Custom)": fig = px.bar(**plot_args, barmode='stack', text_auto=True)
                elif graph_type == "Grouped Bar Graph": fig = px.bar(**plot_args, barmode='group', text_auto=True)
                elif graph_type == "Pie Chart":
                    fig = px.pie(plot_df, names=final_x, values=final_y, color=final_x if color_enc else None, color_discrete_sequence=discrete_seq if color_enc else [custom_color])
                    fig.update_traces(textinfo='label+percent+value')
                elif graph_type == "Donut Chart":
                    fig = px.pie(plot_df, names=final_x, values=final_y, hole=0.4, color=final_x if color_enc else None, color_discrete_sequence=discrete_seq if color_enc else [custom_color])
                    fig.update_traces(textinfo='label+percent+value')
                elif graph_type == "Histogram": fig = px.histogram(**plot_args, text_auto=True) if data_mode == "Raw Data (Individual)" else px.bar(**plot_args, text_auto=True)
                elif graph_type == "Box Plot": fig = px.box(**plot_args)
                elif graph_type == "Violin Plot": fig = px.violin(**plot_args)
                elif graph_type == "Strip Plot": fig = px.strip(**plot_args)
                elif graph_type == "Funnel Chart": fig = px.funnel(**plot_args)
                elif graph_type == "Density Heatmap": fig = px.density_heatmap(**plot_args, text_auto=True)
                
                # CORRELATION ZERO LINE
                if data_mode == "Trend of Correlation Coefficient" and fig:
                    is_y_corr = (final_y == "Correlation")
                    is_x_corr = (final_x == "Correlation")
                    
                    if is_y_corr:
                        fig.add_hline(y=0, line_dash="dash", line_color="black")
                    if is_x_corr:
                        fig.add_vline(x=0, line_dash="dash", line_color="black")

                if fig: st.plotly_chart(fig, use_container_width=True)
                else: st.warning("⚠️ No graph selected.")

            except Exception as e:
                st.warning(f"⚠️ Unable to render this chart configuration. \n\n **Reason:** {e}")
        else:
            if error_message: st.warning(f"⚠️ **Cannot generate plot.** {error_message}")

    else:
        st.info("Please select a Target and Attributes in the sidebar.")
