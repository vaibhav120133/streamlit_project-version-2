import pymysql
import streamlit as st

connection = pymysql.connect(
    host= "localhost",
    user = "root",
    password = "root",
    database = "vehicle_service_db"
)

try:
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users")
    result = cursor.fetchall()
    for row in result:
        print(row)
finally:
    cursor.close()
    connection.close()