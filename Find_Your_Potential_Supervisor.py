import streamlit as st
import pandas as pd

# ==================================================
# PAGE CONFIG
# ==================================================
st.set_page_config(
    page_title="Find Your Potential INHART Supervisor",
    layout="wide"
)

# ==================================================
# LOAD DATA
# ==================================================
@st.cache_data(ttl=10)
def load_data():

    sheet_url = (
        "https://docs.google.com/spreadsheets/d/e/"
        "2PACX-1vSA7NbCZlMbzAkbFerQJc5Nqe8iUYc8N7PsoaMWnMsuJS_v8vA3hQtwvEzZMmLRqU7pi1LUPq0cJ8Hh/pub?output=csv"
    )

    df = pd.read_csv(sheet_url)

    return df


df = load_data()

# ==================================================
# REFRESH BUTTON
# ==================================================
if st.button("Refresh Supervisor Database"):

    st.cache_data.clear()

    st.rerun()

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
# CREATE FINAL NAME
# ==================================================
df["final_name"] = ""

possible_name_columns = [
    "supervisor_name",
    "supervisor_name:",
    "name",
    "name:"
]

for idx, row in df.iterrows():

    final_name = ""

    for col in possible_name_columns:

        if col in df.columns:

            value = str(
                row.get(col, "")
            ).strip()

            if value.lower() not in [
                "",
                "nan",
                "none"
            ]:

                final_name = value
                break

    final_name = (
        final_name
        .replace(".", "")
        .strip()
    )

    final_name = " ".join(
        final_name.split()
    )

    df.at[idx, "final_name"] = final_name

# ==================================================
# REMOVE EMPTY NAMES
# ==================================================
df = df[
    df["final_name"]
    .astype(str)
    .str.strip() != ""
]

# ==================================================
# REMOVE DUPLICATE ROWS
# ==================================================
df = df.drop_duplicates()

# ==================================================
# FIND DEPARTMENT COLUMN
# ==================================================
department_column = ""

for col in df.columns:

    if "department" in col:

        department_column = col
        break

# ==================================================
# CLEAN DEPARTMENT
# ==================================================
if department_column != "":

    df[department_column] = (
        df[department_column]
        .astype(str)
        .str.strip()
    )

# ==================================================
# FIND DIRECTORY COLUMN
# ==================================================
directory_column = ""

for col in df.columns:

    if "directory" in col:

        directory_column = col
        break

# ==================================================
# EXPERTISE COLUMNS
# ==================================================
valid_expertise_columns = []

for col in df.columns:

    if (
        "expertise" in col
        and "level" not in col
    ):

        valid_expertise_columns.append(col)

# ==================================================
# INTEREST COLUMNS
# ==================================================
valid_interest_columns = []

for col in df.columns:

    if (
        "interest" in col
        and "level" not in col
        and "likert" not in col
    ):

        valid_interest_columns.append(col)

# ==================================================
# GROUP SUPERVISORS
# ==================================================
grouped_data = []

unique_supervisors = sorted(
    df["final_name"].unique()
)

for supervisor_name in unique_supervisors:

    supervisor_rows = df[
        df["final_name"] == supervisor_name
    ]

    supervisor_dict = {}

    # ==========================================
    # NAME
    # ==========================================
    supervisor_dict["final_name"] = supervisor_name

    # ==========================================
    # DEPARTMENT
    # ==========================================
    if department_column != "":

        dept_values = (
            supervisor_rows[department_column]
            .dropna()
            .astype(str)
            .str.strip()
            .unique()
            .tolist()
        )

        dept_values = [
            x for x in dept_values
            if x.lower() != "nan"
            and x != ""
        ]

        if len(dept_values) > 0:

            supervisor_dict["department"] = dept_values[0]

        else:

            supervisor_dict["department"] = ""

    else:

        supervisor_dict["department"] = ""

    # ==========================================
    # DIRECTORY
    # ==========================================
    if directory_column != "":

        directory_values = (
            supervisor_rows[directory_column]
            .dropna()
            .astype(str)
            .str.strip()
            .unique()
            .tolist()
        )

        directory_values = [
            x for x in directory_values
            if x.lower() != "nan"
            and x != ""
        ]

        if len(directory_values) > 0:

            supervisor_dict[
                "supervisor_directory"
            ] = directory_values[0]

        else:

            supervisor_dict[
                "supervisor_directory"
            ] = ""

    else:

        supervisor_dict[
            "supervisor_directory"
        ] = ""

    # ==========================================
    # EXPERTISE
    # ==========================================
    expertise_set = set()

    for col in valid_expertise_columns:

        values = (
            supervisor_rows[col]
            .dropna()
            .astype(str)
            .tolist()
        )

        for value in values:

            split_values = value.split(",")

            for item in split_values:

                cleaned_item = (
                    item
                    .strip()
                    .replace("\n", " ")
                    .replace("\r", " ")
                )

                cleaned_lower = cleaned_item.lower()

                if (
                    cleaned_item != ""
                    and cleaned_lower != "nan"
                    and "basic expertise" not in cleaned_lower
                    and "intermediate expertise" not in cleaned_lower
                    and "advanced expertise" not in cleaned_lower
                    and cleaned_lower != "expert"
                ):

                    expertise_set.add(cleaned_item)

    all_expertise = sorted(expertise_set)

    for i, value in enumerate(all_expertise):

        supervisor_dict[
            f"expertise_{i+1}"
        ] = value

    # ==========================================
    # INTERESTS
    # ==========================================
    interest_set = set()

    for col in valid_interest_columns:

        values = (
            supervisor_rows[col]
            .dropna()
            .astype(str)
            .tolist()
        )

        for value in values:

            split_values = value.split(",")

            for item in split_values:

                cleaned_item = (
                    item
                    .strip()
                    .replace("\n", " ")
                    .replace("\r", " ")
                )

                cleaned_lower = cleaned_item.lower()

                if (
                    cleaned_item != ""
                    and cleaned_lower != "nan"
                    and "very interested" not in cleaned_lower
                    and "extremely interested" not in cleaned_lower
                    and "interest_level" not in cleaned_lower
                    and "likert" not in cleaned_lower
                ):

                    interest_set.add(cleaned_item)

    all_interests = sorted(interest_set)

    for i, value in enumerate(all_interests):

        supervisor_dict[
            f"interest_{i+1}"
        ] = value

    grouped_data.append(supervisor_dict)

# ==================================================
# FINAL DATAFRAME
# ==================================================
df = pd.DataFrame(grouped_data)

# ==================================================
# SEARCH TEXT
# ==================================================
search_columns = []

for col in df.columns:

    if (
        col.startswith("expertise_")
        or col.startswith("interest_")
    ):

        search_columns.append(col)

df["combined_text"] = (
    df[search_columns]
    .fillna("")
    .astype(str)
    .agg(" ".join, axis=1)
    .str.lower()
)

# ==================================================
# SIDEBAR
# ==================================================
with st.sidebar:

    st.header("Search & Filter")

    query = st.text_input(
        "Search expertise or research interests"
    )

    departments = sorted(
        [
            x for x in df["department"]
            .dropna()
            .unique()
            .tolist()
            if x != ""
            and str(x).lower() != "nan"
        ]
    )

    selected_department = st.selectbox(
        "Filter by Department",
        ["All"] + departments
    )

    search_button = st.button(
        "Search"
    )

# ==================================================
# TITLE
# ==================================================
st.title(
    "Find Your Potential INHART Supervisor"
)

st.write(
    "Search supervisors based on expertise and research interests."
)

st.markdown("---")

# ==================================================
# GOOGLE FORM
# ==================================================
st.subheader(
    "Supervisor Information Update"
)

st.write(
    "INHART supervisors may update their expertise and research interests using the form below."
)

st.link_button(
    "Fill up supervisor expertise and interest form",
    "https://docs.google.com/forms/d/e/1FAIpQLSeM9bFQZpmFb9nJ3qokIeVT_2ope1O99YlKqQv_rTfDbo8hcA/viewform"
)

st.markdown("---")

# ==================================================
# FILTERING
# ==================================================
filtered_df = df.copy()

if selected_department != "All":

    filtered_df = filtered_df[
        filtered_df["department"]
        == selected_department
    ]

if search_button:

    if query:

        query = query.strip().lower()

        filtered_df = filtered_df[
            filtered_df["combined_text"]
            .str.contains(
                query,
                na=False,
                regex=False
            )
        ]

# ==================================================
# RESULTS
# ==================================================
st.subheader(
    f"Found {len(filtered_df)} supervisors"
)

# ==================================================
# DISPLAY RESULTS
# ==================================================
for _, row in filtered_df.iterrows():

    with st.container(border=True):

        st.markdown(
            f"## {row['final_name']}"
        )

        st.write(
            f"**Department:** {row['department']}"
        )

        # ==========================================
        # EXPERTISE
        # ==========================================
        expertise = []

        for col in row.index:

            if col.startswith("expertise_"):

                value = str(row[col]).strip()

                if (
                    value != ""
                    and value.lower() != "nan"
                ):

                    expertise.append(value)

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
        # INTERESTS
        # ==========================================
        interests = []

        for col in row.index:

            if col.startswith("interest_"):

                value = str(row[col]).strip()

                if (
                    value != ""
                    and value.lower() != "nan"
                ):

                    interests.append(value)

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
        # DIRECTORY BUTTON
        # ==========================================
        directory_link = str(
            row.get("supervisor_directory", "")
        ).strip()

        if (
            directory_link != ""
            and directory_link.lower() != "nan"
        ):

            st.link_button(
                "View IIUM Staff Directory",
                directory_link
            )
