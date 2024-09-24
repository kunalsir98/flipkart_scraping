import mysql.connector 
mydb = mysql.connector.connect(
    host = '',
    user = '', 
    password = ''
)
mycursor = mydb.cursor()
#mycursor.execute('create database flipkart_product_scrap')
mycursor.execute('use flipkart_product_scrap')
mycursor.execute('CREATE TABLE product_reviews (id INT AUTO_INCREMENT PRIMARY KEY,customer_name VARCHAR(255),rating VARCHAR(10),comment TEXT,question TEXT)')
