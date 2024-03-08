import mysql.connector

mydb = mysql.connector.connect(
    host="db5005175800.hosting-data.io",
    user="dbu1422658",
    password="WUYLen9jqHMBWTF1K",  # Replace 'your_password' with your actual password
    database="dbs4329206"
)

cursor = mydb.cursor()
sql = "INSERT INTO xtable (id, name, number, city) VALUES (%s, %s, %s, %s)"
val = ("1", "ahsan2", "12345", "mwi1")  # Values to be inserted

cursor.execute(sql, val)  # Execute the query with values
mydb.commit()              # Commit the changes
mydb.close()               # Close the connection
