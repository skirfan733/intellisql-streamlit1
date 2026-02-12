import streamlit as st
import sqlite3
import os
import pandas as pd
from dotenv import load_dotenv

# Try importing Gemini (will fallback if quota fails)
try:
    from google import genai
    GEMINI_AVAILABLE = True
except:
    GEMINI_AVAILABLE = False


# -------------------------------
# Initialize Database (Cloud Safe)
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

    # Insert sample data only if empty
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


# Call DB initializer
initialize_database()


# -------------------------------
# Setup Gemini (Optional)
# -------------------------------
load_dotenv()

if GEMINI_AVAILABLE and os.getenv("GOOGLE_API_KEY"):
    try:
        client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
    except:
        GEMINI_AVAILABLE = False
else:
    GEMINI_AVAILABLE = False


# -------------------------------
# NL → SQL Generator
# -------------------------------
def generate_sql(question):

    # Try Gemini First
    if GEMINI_AVAILABLE:
        try:
            prompt = f"""
            Convert this question into SQL.
            Table: STUDENTS(name, class, marks, company)
            Return ONLY SQL query.

            Question: {question}
            """

            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt,
            )

            return response.text.strip()

        except:
            pass  # fallback below if quota fails

    # -------------------------------
    # Offline Fallback NLP Logic
    # -------------------------------
    q = question.lower()

    # Detect column
    if "only name" in q or "student name" in q:
        column = "name"
    elif "company" in q:
        column = "company"
    elif "class" in q:
        column = "class"
    else:
        column = "*"

    # Conditions
    if "above" in q or "greater" in q:
        import re
        num = re.findall(r'\d+', q)
        if num:
            return f"SELECT {column} FROM STUDENTS WHERE marks > {num[0]};"

    elif "count" in q or "how many" in q:
        return "SELECT COUNT(*) AS total_students FROM STUDENTS;"

    elif "average" in q:
        return "SELECT AVG(marks) FROM STUDENTS;"

    elif "highest" in q:
        return "SELECT MAX(marks) FROM STUDENTS;"

    elif "all students" in q:
        return "SELECT * FROM STUDENTS;"
    
    elif "average" in q:
        return "SELECT AVG(marks) AS average_marks FROM STUDENTS;"

    elif "highest" in q:
        return "SELECT MAX(marks) AS highest_marks FROM STUDENTS;"

    elif "lowest" in q:
        return "SELECT MIN(marks) AS lowest_marks FROM STUDENTS;"


    else:
        return f"SELECT {column} FROM STUDENTS;"
    


# -------------------------------
# Execute SQL and Return Table
# -------------------------------
def run_query(sql_query):
    conn = sqlite3.connect("data.db")
    df = pd.read_sql_query(sql_query, conn)
    conn.close()
    return df


# -------------------------------
# Streamlit UI
# -------------------------------
st.set_page_config(page_title="IntelliSQL", page_icon="📊")

st.title("📊 IntelliSQL - Natural Language to SQL")
st.write("Ask questions about the Students database.")

question = st.text_input("Enter your question:")

if st.button("Run Query") and question:

    sql_query = generate_sql(question)

    st.subheader("Generated SQL:")
    st.code(sql_query, language="sql")

    try:
        df = run_query(sql_query)

        st.subheader("Query Result:")
        st.dataframe(df, use_container_width=True)

        # Download Button
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download Result as CSV",
            data=csv,
            file_name="query_result.csv",
            mime="text/csv",
        )

    except Exception as e:
        st.error(f"Error executing query: {e}")
