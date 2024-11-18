import pymysql
from dotenv import load_dotenv
import os

load_dotenv()

# Create a connection object
# Database connection class

print(f"DB Name: {os.getenv('DB_NAME')}, User: {os.getenv('DB_USER')}")
class Connection:
    def __init__(self):
        self.con = pymysql.connect(
            database=os.getenv('DB_NAME').strip(),
            user=os.getenv('DB_USER').strip(),
            host=os.getenv('DB_HOST').strip(),
            password=os.getenv('DB_PASSWORD').strip()
        )

        self.cur = self.con.cursor()

    def execute_query(self, query, params=None):
        """Executes a given SQL query with optional parameters."""
        try:
            if params:
                self.cur.execute(query, params)
            else:
                self.cur.execute(query)
            self.con.commit()
            print("Query executed successfully")
        except Exception as e:
            print(f"An error occurred: {e}")
            self.con.rollback()

    def fetch_all(self, query, params=None):
        """Fetches all rows from a query result."""
        try:
            if params:
                self.cur.execute(query, params)
            else:
                self.cur.execute(query)
            return self.cur.fetchall()
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def close(self):
        """Closes the cursor and connection."""
        self.cur.close()
        self.con.close()