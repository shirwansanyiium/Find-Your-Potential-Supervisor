import streamlit as st
import pandas as pd

# Page config
st.set_page_config(
    page_title="Find Your Potential INHART Supervisor",
    layout="wide"
)

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("https://docs.google.com/spreadsheets/d/e/2PACX-1vQYlWSjqnOMP4TjrMBhMeKKluptH6qUzXKt9FIe7U_bi-onh70Fp55n1jcuMWSNlHChzW0OkybKgjkP/pub?output=csv")
    return df

df = load_data()

# Title
st.title("Find Your Potential INHART Supervisor")

st.write(
    "Search supervisors based on expertise and research interests."
)

# Combine searchable text
search_columns = [
    'Expertise 1 ',
    'Expertise 2',
    'Expertise 3',
    'Expertise 4',
    'Expertise 5',
    'Interest 1',
    'Interest 2',
    'Interest 3',
    'Interest 4',
    'Interest 5'
]

df["combined_text"] = (
    df[search_columns]
    .fillna("")
    .astype(str)
    .agg(" ".join, axis=1)
)

# Search bar
query = st.text_input(
    "Search expertise or research interests"
)

# Department filter
departments = (
    df["Department "]
    .dropna()
    .unique()
)

selected_department = st.selectbox(
    "Filter by Department",
    ["All"] + list(departments)
)

# Filtering
filtered_df = df.copy()

if selected_department != "All":
    filtered_df = filtered_df[
        filtered_df["Department "] == selected_department
    ]

if query:
    filtered_df = filtered_df[
        filtered_df["combined_text"]
        .str.contains(
            query,
            case=False,
            na=False
        )
    ]

# Results
st.subheader(
    f"Found {len(filtered_df)} supervisors"
)

for _, row in filtered_df.iterrows():

    with st.container(border=True):

        st.markdown(f"## {row['Name:']}")

        st.write(
            f"**Department:** {row['Department ']}"
        )

        expertise = []

        for i in range(1, 6):

            col = (
                f'Expertise {i}'
                if i > 1
                else 'Expertise 1 '
            )

            if col in row and pd.notna(row[col]):
                expertise.append(row[col])

        interests = []

        for i in range(1, 6):

            col = f'Interest {i}'

            if col in row and pd.notna(row[col]):
                interests.append(row[col])

        st.write("### Expertise")
        st.write(", ".join(expertise))

        st.write("### Research Interests")
        st.write(", ".join(interests))

        if pd.notna(row["Supervisor directory"]):

            st.link_button(
                "View IIUM Directory",
                row["Supervisor directory"]
            )
