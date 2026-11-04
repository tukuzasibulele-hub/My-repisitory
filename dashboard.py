
import sqlite3
import pandas as pd
import streamlit as st

# I connect to my SQLite database.
conn = sqlite3.connect("nextgen.db")

# I set the title and layout of my dashboard.
st.set_page_config(
    page_title="NextGenLearners Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("NextGenLearners Performance Dashboard")
st.write("I use this dashboard to explore applicant, intern and hackathon performance using mock data.")

# I retrieve the available domains from my database.
domains_df = pd.read_sql_query("""
    SELECT DISTINCT domain
    FROM applicants
    WHERE domain IS NOT NULL

    UNION

    SELECT DISTINCT domain
    FROM interns
    WHERE domain IS NOT NULL
""", conn)

domain_options = ["All"] + sorted(domains_df["domain"].dropna().tolist())

# I allow the user to select a domain.
selected_domain = st.selectbox(
    "Select a domain",
    domain_options
)

# I create a condition that filters the selected domain.
if selected_domain == "All":
    domain_condition = ""
else:
    domain_condition = f"WHERE domain = '{selected_domain.replace(chr(39), chr(39) * 2)}'"


# 1. APPLICANT-VERSUS-INTERN FUNNEL


st.header("1. Applicant versus Intern Funnel")

if selected_domain == "All":
    applicant_count = pd.read_sql_query(
        "SELECT COUNT(*) AS total FROM applicants",
        conn
    )["total"].iloc[0]

    intern_count = pd.read_sql_query(
        "SELECT COUNT(*) AS total FROM interns",
        conn
    )["total"].iloc[0]
else:
    applicant_count = pd.read_sql_query(
        "SELECT COUNT(*) AS total FROM applicants WHERE domain = ?",
        conn,
        params=(selected_domain,)
    )["total"].iloc[0]

    intern_count = pd.read_sql_query(
        "SELECT COUNT(*) AS total FROM interns WHERE domain = ?",
        conn,
        params=(selected_domain,)
    )["total"].iloc[0]

funnel_data = pd.DataFrame({
    "Stage": ["Applicants", "Interns"],
    "Number of people": [applicant_count, intern_count]
})

col1, col2 = st.columns(2)

with col1:
    st.metric("Total Applicants", int(applicant_count))

with col2:
    st.metric("Total Interns", int(intern_count))

st.bar_chart(
    funnel_data,
    x="Stage",
    y="Number of people"
)


# 2. COMPLETION RATE PER DOMAIN


st.header("2. Completion Rate per Domain")

completion_query = """
    SELECT
        a.domain,
        COUNT(DISTINCT a.applicant_id) AS total_applicants,
        COUNT(DISTINCT CASE
            WHEN LOWER(TRIM(i.completion_status)) = 'completed'
            THEN i.intern_id
        END) AS completed_interns,
        ROUND(
            100.0 * COUNT(DISTINCT CASE
                WHEN LOWER(TRIM(i.completion_status)) = 'completed'
                THEN i.intern_id
            END) / NULLIF(COUNT(DISTINCT a.applicant_id), 0),
            2
        ) AS completion_rate
    FROM applicants AS a
    LEFT JOIN interns AS i
        ON a.applicant_id = i.applicant_id
    GROUP BY a.domain
    ORDER BY completion_rate DESC
"""

completion_data = pd.read_sql_query(completion_query, conn)

if selected_domain != "All":
    completion_data = completion_data[
        completion_data["domain"] == selected_domain
    ]

st.dataframe(completion_data, use_container_width=True)

st.bar_chart(
    completion_data,
    x="domain",
    y="completion_rate"
)


# 3. AVERAGE HACKATHON SCORE PER DOMAIN


st.header("3. Average Hackathon Score per Domain")

# I join hackathon scores with interns because the domain
# is stored in the interns table, not the scores table.
scores_query = """
    SELECT
        i.domain,
        ROUND(AVG(h.score), 2) AS average_score
    FROM hackathon_scores AS h
    JOIN interns AS i
        ON h.intern_id = i.intern_id
    GROUP BY i.domain
    ORDER BY average_score DESC
"""

scores_data = pd.read_sql_query(scores_query, conn)

# I apply the selected domain filter.
if selected_domain != "All":
    scores_data = scores_data[
        scores_data["domain"] == selected_domain
    ]

st.dataframe(scores_data, use_container_width=True)

if not scores_data.empty:
    st.bar_chart(
        scores_data,
        x="domain",
        y="average_score"
    )
else:
    st.info("There are no hackathon scores for this domain.")

# --------------------------------------------------
# 4. TOP-10 INTERN LEADERBOARD
# --------------------------------------------------

st.header("4. Top-10 Intern Leaderboard")

# I join the three tables to display each intern's name,
# domain and hackathon score.
leaderboard_query = """
    SELECT
        a.applicant_name,
        i.domain,
        h.score
    FROM hackathon_scores AS h
    JOIN interns AS i
        ON h.intern_id = i.intern_id
    JOIN applicants AS a
        ON i.applicant_id = a.applicant_id
    ORDER BY h.score DESC
    LIMIT 10
"""

leaderboard_data = pd.read_sql_query(leaderboard_query, conn)

# I filter the leaderboard using the selected domain.
if selected_domain != "All":
    leaderboard_data = leaderboard_data[
        leaderboard_data["domain"] == selected_domain
    ]

leaderboard_data = leaderboard_data.reset_index(drop=True)
leaderboard_data.index = leaderboard_data.index + 1
leaderboard_data.index.name = "Rank"

st.dataframe(
    leaderboard_data,
    use_container_width=True
)


# 5. COMPLETED VERSUS DROPOUT ANALYSIS


st.header("5. Completed versus Dropout Analysis")

# I count interns according to their completion status.
status_query = """
    SELECT
        domain,
        completion_status,
        COUNT(*) AS total
    FROM interns
    GROUP BY domain, completion_status
    ORDER BY domain
"""

status_data = pd.read_sql_query(status_query, conn)

# I filter the status results using the selected domain.
if selected_domain != "All":
    status_data = status_data[
        status_data["domain"] == selected_domain
    ]

if not status_data.empty:
    status_chart = status_data.pivot(
        index="domain",
        columns="completion_status",
        values="total"
    ).fillna(0)

    st.bar_chart(status_chart)
    st.dataframe(status_data, use_container_width=True)
else:
    st.info("There is no completion-status data to display.")

# I close the database connection after loading the dashboard data.
conn.close()

st.success("Dashboard loaded successfully!")
