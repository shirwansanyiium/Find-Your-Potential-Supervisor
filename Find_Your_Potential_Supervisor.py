import streamlit as st
import pandas as pd

# ==================================================
# PAGE CONFIGURATION
# ==================================================
st.set_page_config(
    page_title="Find Your Potential INHART Supervisor",
    layout="wide"
)

# ==================================================
# TITLE
# ==================================================
st.title("Find Your Potential INHART Supervisor")

st.write(
    "Search supervisors based on expertise and research interests."
)

st.markdown("---")

# ==================================================
# SUPERVISOR UPDATE SECTION
# ==================================================
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

# ==================================================
# LOAD DATA
# ==================================================
@st.cache_data
def load_data():

    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQYlWSjqnOMP4TjrMBhMeKKluptH6qUzXKt9FIe7U_bi-onh70Fp55n1jcuMWSNlHChzW0OkybKgjkP/pub?output=csv"

    df = pd.read_csv(url)

    return df


df = load_data()

# ==================================================
# CLEAN COLUMN NAMES
# ==================================================
df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")
)

# ==================================================
# REMOVE EMPTY ROWS
# ==================================================
df = df.dropna(how="all")

# ==================================================
# REQUIRED COLUMNS
# ==================================================
required_columns = [
    "name:",
    "department"
]

for col in required_columns:

    if col not in df.columns:

        st.error(f"Missing required column: {col}")
        st.stop()

# ==================================================
# FILL MISSING VALUES
# ==================================================
df = df.fillna("")

# ==================================================
# COMBINE DUPLICATE SUPERVISORS
# ==================================================
grouped_rows = []

# Group by supervisor name
grouped = df.groupby("name:")

for supervisor_name, group in grouped:

    combined_row = {}

    # Keep supervisor name
    combined_row["name:"] = supervisor_name

    # Keep first department
    if "department" in group.columns:

        departments = (
            group["department"]
            .astype(str)
            .str.strip()
            .unique()
        )

        departments = [
            d for d in departments
            if d != ""
        ]

        combined_row["department"] = ", ".join(departments)

    # ==================================================
    # COMBINE EXPERTISE
    # ==================================================
    expertise_set = set()

    for i in range(1, 6):

        col = f"expertise_{i}"

        if col in group.columns:

            for value in group[col]:

                value = str(value).strip()

                if value != "":
                    expertise_set.add(value)

    expertise_list = sorted(list(expertise_set))

    # Store expertise into columns
    for idx, value in enumerate(expertise_list[:20], start=1):

        combined_row[f"expertise_{idx}"] = value

    # ==================================================
    # COMBINE INTERESTS
    # ==================================================
    interest_set = set()

    for i in range(1, 6):

        col = f"interest_{i}"

        if col in group.columns:

            for value in group[col]:

                value = str(value).strip()

                if value != "":
                    interest_set.add(value)

    interest_list = sorted(list(interest_set))

    # Store interests into columns
    for idx, value in enumerate(interest_list[:20], start=1):

        combined_row[f"interest_{idx}"] = value

    # ==================================================
    # SUPERVISOR DIRECTORY
    # ==================================================
    if "supervisor_directory" in group.columns:

        directories = (
            group["supervisor_directory"]
            .astype(str)
            .str.strip()
            .unique()
        )

        directories = [
            d for d in directories
            if d != ""
        ]

        if len(directories) > 0:

            combined_row["supervisor_directory"] = directories[0]

    grouped_rows.append(combined_row)

# ==================================================
# CREATE CLEAN DATAFRAME
# ==================================================
df = pd.DataFrame(grouped_rows)

# ==================================================
# SEARCHABLE COLUMNS
# ==================================================
search_columns = []

for col in df.columns:

    if (
        "expertise_" in col
        or "interest_" in col
    ):

        search_columns.append(col)

# ==================================================
# COMBINE SEARCH TEXT
# ==================================================
df["combined_text"] = (
    df[search_columns]
    .fillna("")
    .astype(str)
    .agg(" ".join, axis=1)
)

# ==================================================
# SIDEBAR SEARCH
# ==================================================
st.sidebar.header("Search & Filter")

query = st.sidebar.text_input(
    "Search expertise or research interests"
)

# ==================================================
# DEPARTMENT FILTER
# ==================================================
departments = sorted(
    df["department"]
    .dropna()
    .unique()
)

selected_department = st.sidebar.selectbox(
    "Filter by Department",
    ["All"] + list(departments)
)

# ==================================================
# FILTERING
# ==================================================
filtered_df = df.copy()

# Department filter
if selected_department != "All":

    filtered_df = filtered_df[
        filtered_df["department"]
        == selected_department
    ]

# Search filter
if query:

    filtered_df = filtered_df[
        filtered_df["combined_text"]
        .str.contains(
            query,
            case=False,
            na=False
        )
    ]

# ==================================================
# RESULTS
# ==================================================
st.subheader(
    f"Found {len(filtered_df)} supervisors"
)

# ==================================================
# DISPLAY SUPERVISORS
# ==================================================
for _, row in filtered_df.iterrows():

    with st.container(border=True):

        # ==========================================
        # NAME
        # ==========================================
        st.markdown(
            f"## {row['name:']}"
        )

        # ==========================================
        # DEPARTMENT
        # ==========================================
        st.write(
            f"**Department:** {row['department']}"
        )

        # ==========================================
        # EXPERTISE
        # ==========================================
        expertise = []

        for col in row.index:

            if "expertise_" in col:

                value = str(row[col]).strip()

                if value != "":
                    expertise.append(value)

        st.write("### Expertise")

        if len(expertise) > 0:

            st.write(
                ", ".join(sorted(expertise))
            )

        else:

            st.write(
                "No expertise information available."
            )

        # ==========================================
        # RESEARCH INTERESTS
        # ==========================================
        interests = []

        for col in row.index:

            if "interest_" in col:

                value = str(row[col]).strip()

                if value != "":
                    interests.append(value)

        st.write("### Research Interests")

        if len(interests) > 0:

            st.write(
                ", ".join(sorted(interests))
            )

        else:

            st.write(
                "No research interest information available."
            )

        # ==========================================
        # IIUM DIRECTORY
        # ==========================================
        if (
            "supervisor_directory" in row.index
            and str(row["supervisor_directory"]).strip() != ""
        ):

            st.link_button(
                "View IIUM Directory",
                row["supervisor_directory"]
            )
