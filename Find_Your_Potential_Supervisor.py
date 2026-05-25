```python id="ps4y8m"
import streamlit as st
import pandas as pd

# ====================================
# PAGE CONFIGURATION
# ====================================
st.set_page_config(
    page_title="Find Your Potential INHART Supervisor",
    layout="wide"
)

# ====================================
# TITLE
# ====================================
st.title("Find Your Potential INHART Supervisor")

st.write(
    "Search supervisors based on expertise and research interests."
)

st.markdown("---")

# ====================================
# SUPERVISOR UPDATE SECTION
# ====================================
st.markdown(
    """
    ### Supervisor Information Update

    INHART supervisors may update their expertise and research interests using the form below.
    """
)

st.link_button(
    "Fill Up Supervisor Expertise Form",
    "https://docs.google.com/forms/d/e/1FAIpQLSf4yW4mbvcU7wEkNtR5NzINus-WCWnBhhK-2YH-fV85D_E7Mg/viewform?usp=preview"
)

st.markdown("---")

# ====================================
# LOAD DATA
# ====================================
@st.cache_data
def load_data():

    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQYlWSjqnOMP4TjrMBhMeKKluptH6qUzXKt9FIe7U_bi-onh70Fp55n1jcuMWSNlHChzW0OkybKgjkP/pub?output=csv"

    df = pd.read_csv(url)

    return df


df = load_data()

# ====================================
# CLEAN COLUMN NAMES
# ====================================
df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")
)

# ====================================
# SEARCHABLE COLUMNS
# ====================================
search_columns = [
    "expertise_1",
    "expertise_2",
    "expertise_3",
    "expertise_4",
    "expertise_5",
    "interest_1",
    "interest_2",
    "interest_3",
    "interest_4",
    "interest_5"
]

# Keep only columns that exist
search_columns = [
    col for col in search_columns
    if col in df.columns
]

# ====================================
# COMBINE SEARCH TEXT
# ====================================
df["combined_text"] = (
    df[search_columns]
    .fillna("")
    .astype(str)
    .agg(" ".join, axis=1)
)

# ====================================
# SIDEBAR SEARCH
# ====================================
st.sidebar.header("Search & Filter")

query = st.sidebar.text_input(
    "Search expertise or research interests"
)

# ====================================
# DEPARTMENT FILTER
# ====================================
if "department" in df.columns:

    departments = sorted(
        df["department"]
        .dropna()
        .unique()
    )

    selected_department = st.sidebar.selectbox(
        "Filter by Department",
        ["All"] + list(departments)
    )

else:

    selected_department = "All"

# ====================================
# FILTERING
# ====================================
filtered_df = df.copy()

# Department filtering
if (
    selected_department != "All"
    and "department" in filtered_df.columns
):

    filtered_df = filtered_df[
        filtered_df["department"]
        == selected_department
    ]

# Search filtering
if query:

    filtered_df = filtered_df[
        filtered_df["combined_text"]
        .str.contains(
            query,
            case=False,
            na=False
        )
    ]

# ====================================
# RESULTS
# ====================================
st.subheader(
    f"Found {len(filtered_df)} supervisors"
)

# ====================================
# DISPLAY SUPERVISORS
# ====================================
for _, row in filtered_df.iterrows():

    with st.container(border=True):

        # ----------------------------
        # NAME
        # ----------------------------
        if "name:" in row.index:

            st.markdown(
                f"## {row['name:']}"
            )

        # ----------------------------
        # DEPARTMENT
        # ----------------------------
        if "department" in row.index:

            st.write(
                f"**Department:** {row['department']}"
            )

        # ----------------------------
        # EXPERTISE
        # ----------------------------
        expertise = []

        for i in range(1, 6):

            col = f"expertise_{i}"

            if (
                col in row.index
                and pd.notna(row[col])
            ):

                expertise.append(
                    str(row[col])
                )

        st.write("### Expertise")

        if expertise:

            st.write(
                ", ".join(expertise)
            )

        else:

            st.write(
                "No expertise information available."
            )

        # ----------------------------
        # RESEARCH INTERESTS
        # ----------------------------
        interests = []

        for i in range(1, 6):

            col = f"interest_{i}"

            if (
                col in row.index
                and pd.notna(row[col])
            ):

                interests.append(
                    str(row[col])
                )

        st.write("### Research Interests")

        if interests:

            st.write(
                ", ".join(interests)
            )

        else:

            st.write(
                "No research interest information available."
            )

        # ----------------------------
        # IIUM DIRECTORY LINK
        # ----------------------------
        if "supervisor_directory" in row.index:

            if pd.notna(row["supervisor_directory"]):

                st.link_button(
                    "View IIUM Directory",
                    row["supervisor_directory"]
                )
```
