import streamlit as st
import sqlite3
import os
from dotenv import load_dotenv
from google import genai

# Load API key
load_dotenv()

# Create Gemini client
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

initialize_database()
# -------------------------------
# Create Database if Not Exists
# -------------------------------
def initialize_database():
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS STUDENTS(
        name TEXT,
        class TEXT,
        marks INTEGER,
        company TEXT
    )
    """)

    # Insert sample data only if table is empty
    cursor.execute("SELECT COUNT(*) FROM STUDENTS")
    if cursor.fetchone()[0] == 0:
        students_data = [
            ("Sijo", "BTech", 75, "JSW"),
            ("Lijo", "MTech", 69, "TCS"),
            ("Rijo", "BSC", 79, "WIPRO"),
            ("Sibi", "MSC", 89, "INFOSYS"),
            ("Dilsha", "MCOM", 99, "CYIENT")
        ]
        cursor.executemany("INSERT INTO STUDENTS VALUES (?,?,?,?)", students_data)

    conn.commit()
    conn.close()


# -------------------------------
# Function: Convert NL → SQL
# -------------------------------
def generate_sql(question):
    prompt = f"""
    You are an expert in converting English questions into SQL queries.

    Database: STUDENTS
    Columns:
    name, class, marks, company

    Convert the question into ONLY SQL query.
    Do not explain anything.

    Question: {question}
    """

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
    )

    return response.text.strip()

# -------------------------------
# Execute SQL Query
# -------------------------------
def run_query(sql_query):
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    cursor.execute(sql_query)
    rows = cursor.fetchall()
    conn.close()
    return rows

# -------------------------------
# Streamlit UI
# -------------------------------
st.title("📊 IntelliSQL - Natural Language to SQL")

question = st.text_input("Ask a question about Students database:")

if st.button("Run Query"):
    if question:
        sql_query = generate_sql(question)

        st.subheader("Generated SQL:")
        st.code(sql_query, language="sql")

        try:
            result = run_query(sql_query)
            st.subheader("Result:")
            for row in result:
                st.write(row)
        except Exception as e:
            st.error(f"SQL Error: {e}")
