import sqlite3

# Connect to SQLite database
connection = sqlite3.connect("data.db")
cursor = connection.cursor()

# Create STUDENTS table
cursor.execute("""
CREATE TABLE IF NOT EXISTS STUDENTS(
    name TEXT,
    class TEXT,
    marks INTEGER,
    company TEXT
)
""")

# Insert sample data
students_data = [
    ("Sijo", "BTech", 75, "JSW"),
    ("Lijo", "MTech", 69, "TCS"),
    ("Rijo", "BSC", 79, "WIPRO"),
    ("Sibi", "MSC", 89, "INFOSYS"),
    ("Dilsha", "MCOM", 99, "CYIENT")
]

cursor.executemany("INSERT INTO STUDENTS VALUES (?,?,?,?)", students_data)

connection.commit()
connection.close()

print("Database Created Successfully!")
