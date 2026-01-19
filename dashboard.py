import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# -------------------------------
# Page configuration
# -------------------------------
st.set_page_config(
    page_title="AI Agents Ecosystem Dashboard",
    layout="wide"
)

st.title("📊 AI Agents Ecosystem Dashboard (2026)")
st.markdown(
    """
    This interactive dashboard explores trends, sources, and content types 
    within the AI Agents ecosystem using real-world data.
    """
)

# -------------------------------
# Load data
# -------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("AI_Agents_Ecosystem_2026.csv")
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    return df

df = load_data()

# -------------------------------
# Feature Engineering
# -------------------------------
def classify_content(text):
    text = str(text).lower()
    if 'job' in text or 'hiring' in text or 'engineer' in text:
        return 'Job Posting'
    elif 'open-source' in text or 'github' in text or 'tool' in text:
        return 'Tool / Project'
    else:
        return 'News / Discussion'

df['Content_Type'] = df['Title'].apply(classify_content)
df['Description_Length'] = df['Description'].astype(str).apply(len)

# -------------------------------
# Sidebar filters
# -------------------------------
st.sidebar.header("🔎 Filters")

source_filter = st.sidebar.multiselect(
    "Select Source(s)",
    options=df['Source'].unique(),
    default=df['Source'].unique()
)

content_filter = st.sidebar.multiselect(
    "Select Content Type(s)",
    options=df['Content_Type'].unique(),
    default=df['Content_Type'].unique()
)

date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(df['Date'].min(), df['Date'].max())
)

filtered_df = df[
    (df['Source'].isin(source_filter)) &
    (df['Content_Type'].isin(content_filter)) &
    (df['Date'] >= pd.to_datetime(date_range[0])) &
    (df['Date'] <= pd.to_datetime(date_range[1]))
]

st.markdown(f"**Total records:** {len(filtered_df)}")

# -------------------------------
# Layout: two columns
# -------------------------------
col1, col2 = st.columns(2)

# -------------------------------
# Chart 1: Posts by Source
# -------------------------------
with col1:
    st.subheader("Posts by Source")
    source_counts = filtered_df['Source'].value_counts()

    fig, ax = plt.subplots()
    source_counts.plot(kind='bar', ax=ax)
    ax.set_ylabel("Count")
    ax.set_xlabel("Source")
    st.pyplot(fig)

# -------------------------------
# Chart 2: Content Type Distribution
# -------------------------------
with col2:
    st.subheader("Content Type Distribution")
    content_counts = filtered_df['Content_Type'].value_counts()

    fig, ax = plt.subplots()
    content_counts.plot(kind='pie', autopct='%1.1f%%', ax=ax)
    ax.set_ylabel("")
    st.pyplot(fig)

# -------------------------------
# Chart 3: Posts Over Time
# -------------------------------
st.subheader("Posts Over Time")

time_series = (
    filtered_df
    .groupby(filtered_df['Date'].dt.to_period('M'))
    .size()
)
time_series.index = time_series.index.to_timestamp()

fig, ax = plt.subplots(figsize=(10, 4))
time_series.plot(ax=ax)
ax.set_ylabel("Number of Posts")
ax.set_xlabel("Date")
st.pyplot(fig)

# -------------------------------
# Chart 4: Description Length by Content Type
# -------------------------------
st.subheader("Description Length by Content Type")

fig, ax = plt.subplots(figsize=(8, 4))
sns.boxplot(
    data=filtered_df,
    x='Content_Type',
    y='Description_Length',
    ax=ax
)
ax.set_xlabel("Content Type")
ax.set_ylabel("Characters")
st.pyplot(fig)

# -------------------------------
# Chart 5: Job Postings Over Time
# -------------------------------
st.subheader("Job Postings Over Time")

jobs_df = filtered_df[filtered_df['Content_Type'] == 'Job Posting']

if not jobs_df.empty:
    job_time = (
        jobs_df
        .groupby(jobs_df['Date'].dt.to_period('M'))
        .size()
    )
    job_time.index = job_time.index.to_timestamp()

    fig, ax = plt.subplots(figsize=(10, 4))
    job_time.plot(ax=ax)
    ax.set_ylabel("Job Posts")
    ax.set_xlabel("Date")
    st.pyplot(fig)
else:
    st.info("No job postings available for the selected filters.")

# -------------------------------
# Raw data preview
# -------------------------------
st.subheader("📄 Data Preview")
st.dataframe(filtered_df.head(20))
