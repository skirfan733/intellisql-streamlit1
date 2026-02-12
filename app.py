import streamlit as st
import sqlite3
import os
from dotenv import load_dotenv
from google import genai
import pandas as pd

# Load API key
load_dotenv()

# Create Gemini client
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))


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

initialize_database()
# -------------------------------
# Function: Convert NL → SQL
# -------------------------------
def generate_sql(question):
    """
    Try Gemini first.
    If API fails (cloud quota issue), use fallback logic.
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=question,
        )
        return response.text.strip()

    except Exception:
        # -------- FALLBACK (Runs on Streamlit Cloud) --------
        q = question.lower()

        if "all students" in q:
            return "SELECT * FROM STUDENTS;"

        elif "count" in q or "how many" in q:
            return "SELECT COUNT(*) FROM STUDENTS;"

        elif "above" in q or "greater" in q:
            import re
            num = re.findall(r'\d+', q)
            if num:
                return f"SELECT * FROM STUDENTS WHERE marks > {num[0]};"

        elif "company" in q:
            return "SELECT name, company FROM STUDENTS;"

        else:
            return "SELECT * FROM STUDENTS;"


# -------------------------------
# Execute SQL Query
# -------------------------------
def run_query(sql_query):
    conn = sqlite3.connect("data.db")

    # Read query into dataframe
    df = pd.read_sql_query(sql_query, conn)

    conn.close()
    return df

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
            df = run_query(sql_query)

            st.subheader("Query Result:")
            st.dataframe(df, use_container_width=True)

        except Exception as e:
            st.error(f"SQL Error: {e}")
csv = df.to_csv(index=False).encode('utf-8')
st.download_button(
    "Download as CSV",
    csv,
    "students_result.csv",
    "text/csv"
)
