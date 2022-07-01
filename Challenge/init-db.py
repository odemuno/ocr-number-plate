# initialize our database to the schema we want
# setting up tables, populating them with values, and so on. 

import mysql.connector as mysql
import os
import datetime
from dotenv import load_dotenv #only required if using dotenv for creds
 
load_dotenv()
db_host = os.environ['MYSQL_HOST']
db_user = os.environ['MYSQL_USER']
db_pass = os.environ['MYSQL_PASSWORD']
 
db = mysql.connect(user=db_user, password=db_pass, host=db_host)
cursor = db.cursor()
 
# Create a new database
cursor.execute("CREATE DATABASE IF NOT EXISTS Lab7;")
cursor.execute("USE Lab7")

# dropping: an irrevocable action, and cannot be undone
cursor.execute("DROP TABLE IF EXISTS PlateData;")
 
# Create table
try:
  cursor.execute("""
    CREATE TABLE PlateData (
      id          integer  AUTO_INCREMENT PRIMARY KEY,
      created_at TIMESTAMP,
      image_name    VARCHAR(50),
      text_detected VARCHAR(50)
    );
  """)

# in case our query is not executed but throws an error
# we want to know what the error was at the MySQL end
except RuntimeError as err:
  print("runtime error: {0}".format(err))

# insert data in detector.py