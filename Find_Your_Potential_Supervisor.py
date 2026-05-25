Here is the FULL UPDATED code with ALL fixes integrated together:
• Google Sheets loading
• duplicate supervisor merging
• `name:` + `supervisor_name` support
• remove `nan`
• combine repeated expertise/interests
• safer loading
• cleaner display
• sidebar filtering
• IIUM directory button support



```python
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

    try:

        df = pd.read_csv(url)

        return df

    except Exception as e:

        st.error(
            "Failed to load Google Sheets data."
        )

        st.exception(e)

        return pd.DataFrame()


df = load_data()

# Stop app if dataframe empty
if df.empty:

    st.stop()

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
# FILL MISSING VALUES
# ==================================================
df = df.fillna("")

# ==================================================
# CREATE FINAL NAME COLUMN
# ==================================================
df["final_name"] = ""

for idx, row in df.iterrows():

    primary_name = ""

    secondary_name = ""

    # ----------------------------------------------
    # NAME:
    # ----------------------------------------------
    if "name:" in df.columns:

        primary_name = str(
            row["name:"]
        ).strip()

    # ----------------------------------------------
    # SUPERVISOR_NAME
    # ----------------------------------------------
    if "supervisor_name" in df.columns:

        secondary_name = str(
            row["supervisor_name"]
        ).strip()

    # Remove nan
    if primary_name.lower() == "nan":
        primary_name = ""

    if secondary_name.lower() == "nan":
        secondary_name = ""

    # Priority
    if primary_name != "":

        df.at[idx, "final_name"] = primary_name

    elif secondary_name != "":

        df.at[idx, "final_name"] = secondary_name

# Remove empty names
df = df[
    df["final_name"].str.strip() != ""
]

# ==================================================
# COMBINE DUPLICATE SUPERVISORS
# ==================================================
grouped_rows = []

grouped = df.groupby("final_name")

for supervisor_name, group in grouped:

    combined_row = {}

    # ==============================================
    # NAME
    # ==============================================
    combined_row["final_name"] = supervisor_name

    # ==============================================
    # DEPARTMENT
    # ==============================================
    departments = []

    if "department" in group.columns:

        for value in group["department"]:

            value = str(value).strip()

            if (
                value != ""
                and value.lower() != "nan"
                and value not in departments
            ):

                departments.append(value)

    combined_row["department"] = ", ".join(departments)

    # ==============================================
    # COMBINE EXPERTISE
    # ==============================================
    expertise_set = set()

    for col in group.columns:

        if "expertise_" in col:

            for value in group[col]:

                value = str(value).strip()

                if (
                    value != ""
                    and value.lower() != "nan"
                ):

                    expertise_set.add(value)

    expertise_list = sorted(
        list(expertise_set)
    )

    for idx2, value in enumerate(
        expertise_list,
        start=1
    ):

        combined_row[
            f"expertise_{idx2}"
        ] = value

    # ==============================================
    # COMBINE RESEARCH INTERESTS
    # ==============================================
    interest_set = set()

    for col in group.columns:

        if "interest_" in col:

            for value in group[col]:

                value = str(value).strip()

                if (
                    value != ""
                    and value.lower() != "nan"
                ):

                    interest_set.add(value)

    interest_list = sorted(
        list(interest_set)
    )

    for idx2, value in enumerate(
        interest_list,
        start=1
    ):

        combined_row[
            f"interest_{idx2}"
        ] = value

    # ==============================================
    # SUPERVISOR DIRECTORY
    # ==============================================
    if "supervisor_directory" in group.columns:

        directories = []

        for value in group[
            "supervisor_directory"
        ]:

            value = str(value).strip()

            if (
                value != ""
                and value.lower() != "nan"
                and value not in directories
            ):

                directories.append(value)

        if len(directories) > 0:

            combined_row[
                "supervisor_directory"
            ] = directories[0]

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
            f"## {row['final_name']}"
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

                if (
                    value != ""
                    and value.lower() != "nan"
                ):

                    expertise.append(value)

        # Remove duplicates
        expertise = list(dict.fromkeys(expertise))

        st.write("### Expertise")

        if len(expertise) > 0:

            st.write(
                ", ".join(expertise)
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

                if (
                    value != ""
                    and value.lower() != "nan"
                ):

                    interests.append(value)

        # Remove duplicates
        interests = list(dict.fromkeys(interests))

        st.write("### Research Interests")

        if len(interests) > 0:

            st.write(
                ", ".join(interests)
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
```
