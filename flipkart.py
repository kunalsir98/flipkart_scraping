import mysql.connector as conn
mydb = conn.connect(host = '', user = '', password = '')
mydb
mycursor = mydb.cursor()
mycursor.execute('SHOW DATABASES')
for x in mycursor:
    print(x)
cursor=mydb.cursor()
cursor.execute('create database scraping')






