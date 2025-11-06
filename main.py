import mysql.connector
import os
import rdkit

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password=os.environ.get("SQL_PW"),
    database="ts-predict-db"
)