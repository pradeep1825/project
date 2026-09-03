"""
config.py
----------
This file holds the MySQL connection settings and a helper function
that Flask uses to talk to the database.

TELUGU: Idi MySQL database ki connect avvadaniki config settings
pedathamu. Ee function ni app.py lo call chesi DB connection thistham.
"""

import mysql.connector
from mysql.connector import Error

# ------------- CHANGE THESE VALUES AS PER YOUR MYSQL SETUP -------------
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "your_mysql_password",   # <-- change this
    "database": "banking_system"
}
# -------------------------------------------------------------------------


def get_db_connection():
    """
    Opens and returns a new MySQL connection.
    Every route that needs the database calls this function,
    uses the connection, and then closes it.
    """
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print("Database connection failed:", e)
        return None
