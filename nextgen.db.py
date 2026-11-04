import sqlite3

# connecting to the database file
conn = sqlite3.connect("nextgen.db")
cursor = conn.cursor()

# Removing old tables so the script can be run again safely
cursor.executescript("""
DROP TABLE IF EXISTS hackathon_scores;
DROP TABLE IF EXISTS interns;
DROP TABLE IF EXISTS applicants;
""")
# creating the applicant table
cursor.execute("""
CREATE TABLE applicants (
    applicant_id INTEGER PRIMARY KEY,
    applicant_name TEXT NOT NULL,
    domain TEXT NOT NULL
)
""")

# creating the interns table
cursor.execute("""
CREATE TABLE interns (
    intern_id INTEGER PRIMARY KEY,
    applicant_id INTEGER NOT NULL,
    domain TEXT NOT NULL,
    completion_status TEXT NOT NULL,
    FOREIGN KEY (applicant_id) REFERENCES applicants(applicant_id)
)
""")
# creating the hackathon table
cursor.execute("""
CREATE TABLE hackathon_scores (
    score_id INTEGER PRIMARY KEY,
    intern_id INTEGER NOT NULL,
    score REAL NOT NULL,
    FOREIGN KEY (intern_id) REFERENCES interns(intern_id)
)
""")

# mock applicant data
applicants = [
    (1, "Thabo Mokoena", "Data Science"),
    (2, "Lerato Dlamini", "Data Science"),
    (3, "Ayanda Nkosi", "Data Science"),
    (4, "Sipho Khumalo", "Software Development"),
    (5, "Naledi Molefe", "Software Development"),
    (6, "Bongani Zulu", "Software Development"),
    (7, "Zanele Ndlovu", "Cybersecurity"),
    (8, "Kagiso Maseko", "Cybersecurity"),
    (9, "Luyanda Mthembu", "Cybersecurity"),
    (10, "Amara Jacobs", "Cloud Computing"),
    (11, "Musa Dube", "Cloud Computing"),
    (12, "Palesa Sithole", "Cloud Computing"),
    (13, "Siyabonga Cele", "Data Science"),
    (14, "Keabetswe Modise", "Software Development"),
    (15, "Nokuthula Nene", "Cybersecurity"),
    (16, "Tshepo Radebe", "Cloud Computing"),
    (17, "Anele Gqirana", "Data Science"),
    (18, "Refilwe Baloyi", "Software Development")
]

cursor.executemany("""
INSERT INTO applicants (applicant_id, applicant_name, domain)
VALUES (?, ?, ?)
""", applicants)

#  Insert mock interns
# Some interns completed the programme; others dropped out or are still active.
interns = [
    (101, 1, "Data Science", "Completed"),
    (102, 2, "Data Science", "Completed"),
    (103, 4, "Software Development", "Completed"),
    (104, 5, "Software Development", "Dropped Out"),
    (105, 7, "Cybersecurity", "Completed"),
    (106, 8, "Cybersecurity", "In Progress"),
    (107, 10, "Cloud Computing", "Completed"),
    (108, 11, "Cloud Computing", "Dropped Out"),
    (109, 13, "Data Science", "Completed"),
    (110, 14, "Software Development", "Completed"),
    (111, 15, "Cybersecurity", "Completed"),
    (112, 16, "Cloud Computing", "Completed")
]

cursor.executemany("""
INSERT INTO interns
(intern_id, applicant_id, domain, completion_status)
VALUES (?, ?, ?, ?)
""", interns)

#  Insert mock hackathon scores
scores = [
    (1, 101, 92),
    (2, 102, 78),
    (3, 103, 88),
    (4, 104, 65),
    (5, 105, 95),
    (6, 106, 72),
    (7, 107, 90),
    (8, 108, 68),
    (9, 109, 85),
    (10, 110, 91),
    (11, 111, 87),
    (12, 112, 83)
]

cursor.executemany("""
INSERT INTO hackathon_scores (score_id, intern_id, score)
VALUES (?, ?, ?)
""", scores)

# Save changes and close the database
conn.commit()
conn.close()
# checking if database created successfully
print("Mock data successfully created in nextgen.db")
