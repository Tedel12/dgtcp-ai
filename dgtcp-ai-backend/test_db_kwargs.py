import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

print("Testing connection with keyword arguments...")

try:
    conn = psycopg2.connect(
        dbname="dgtcp_ai",
        user="postgres",
        password="postgres",
        host="localhost",
        port="5432"
    )
    print("Connection successful!")
    conn.close()
except Exception as e:
    print(f"Error type: {type(e)}")
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
