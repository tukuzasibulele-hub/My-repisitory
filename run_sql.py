
import sqlite3

# I connect to my SQLite database.
conn = sqlite3.connect("nextgen.db")
cursor = conn.cursor()

# I store my SQL queries in a list so I can run them one after another.
queries = [

    # QUERY 1: How many interns completed the programme in each domain?
    (
        "Completed interns per domain",
        """
        SELECT
            domain,
            COUNT(*) AS completed_interns
        FROM interns
        WHERE completion_status = 'Completed'
        GROUP BY domain
        ORDER BY completed_interns DESC
        """
    ),

    # QUERY 2: What is the average hackathon score for each domain?
    (
        "Average hackathon score per domain",
        """
        SELECT
            i.domain,
            ROUND(AVG(h.score), 2) AS average_score
        FROM hackathon_scores AS h
        JOIN interns AS i
            ON h.intern_id = i.intern_id
        GROUP BY i.domain
        ORDER BY average_score DESC
        """
    ),

    # QUERY 3: Which interns achieved a hackathon score of at least 85?
    (
        "Top-performing interns",
        """
        SELECT
            a.applicant_name,
            i.domain,
            h.score
        FROM hackathon_scores AS h
        JOIN interns AS i
            ON h.intern_id = i.intern_id
        JOIN applicants AS a
            ON i.applicant_id = a.applicant_id
        WHERE h.score >= 85
        ORDER BY h.score DESC
        """
    )
]

# I execute each query and display its results.
for title, query in queries:
    print("\n" + title)
    print("-" * 40)

    cursor.execute(query)

    for row in cursor.fetchall():
        print(row)

# I close the database connection after running my queries.
conn.close()
