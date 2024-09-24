import time
from flask import Flask, render_template, request, send_file
from flask_cors import CORS, cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import mysql.connector
from mysql.connector import Error
import csv

app = Flask(__name__)
CORS(app)

# Database connection configuration
db_config = {
    'host': '',
    'user': '',
    'password': '',
    'database': 'flipkart_product_scrap'
}

def connect_db():
    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error: {e}")
        return None

def insert_data(customer_names, ratings, comments, questions):
    connection = connect_db()
    if connection:
        cursor = connection.cursor()
        for i in range(len(ratings)):
            cursor.execute(
                "INSERT INTO product_reviews (customer_name, rating, comment, question) VALUES (%s, %s, %s, %s)",
                (customer_names[i] if len(customer_names) > i else '',
                 ratings[i] if len(ratings) > i else '',
                 comments[i] if len(comments) > i else '',
                 questions[i] if len(questions) > i else '')
            )
        connection.commit()
        cursor.close()
        connection.close()

# Function to scrape data
def scrape_flipkart(search_string):
    flipkart_url = 'https://www.flipkart.com/search?q=' + search_string.replace(" ", "%20")
    
    # Delay of 2 seconds before sending the request
    time.sleep(9)
    uclient = uReq(flipkart_url)
    flipkartpage = uclient.read()
    uclient.close()
    flipkart_html = bs(flipkartpage, 'html.parser')

    links = flipkart_html.findAll('a', attrs={'class':'VJA3rP'})
    product_link = 'https://www.flipkart.com' + links[0].get('href')

    # Delay of 2 seconds before sending the next request
    time.sleep(9 )
    new_link = uReq(product_link)
    URL = bs(new_link, 'html.parser')
    new_link.close()

    comments = URL.find_all('div', {'class': "RcXBOT"})
    ratings = []
    customer_names = []
    customer_comments = []
    customer_questions = []

    for comment in comments:
        try:
            ratings.append(comment.div.div.div.div.text)
            customer_comments.append(comment.div.find_all('div',{'class':"ZmyHeo"})[0].div.text)
            customer_names.append(comment.div.div.find_all('p',{'class':"_2NsDsF AwS1CA"})[0].text)
        except:
            pass

    questions = URL.find_all('div', {'class': "BZMA+t"})
    for question in questions:
        try:
            customer_questions.append(question.div.find_all('div',{'class':'wys2hv _43gOsC'})[0].text)
        except:
            pass

    return customer_names, ratings, customer_comments, customer_questions

@app.route('/', methods=['GET', 'POST'])
@cross_origin()
def index():
    if request.method == 'POST':
        search_string = request.form['search']
        customer_names, ratings, customer_comments, customer_questions = scrape_flipkart(search_string)
        insert_data(customer_names, ratings, customer_comments, customer_questions)
        return render_template('result.html', customer_names=customer_names, ratings=ratings, comments=customer_comments, questions=customer_questions)
    return render_template('index.html')

@app.route('/download_csv/<search>', methods=['GET'])
def download_csv(search):
    customer_names, ratings, customer_comments, customer_questions = scrape_flipkart(search)
    filename = f"{search}_results.csv"

    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['Customer Name', 'Rating', 'Comment', 'Question'])
        for i in range(len(ratings)):
            csvwriter.writerow([
                customer_names[i] if len(customer_names) > i else '',
                ratings[i] if len(ratings) > i else '',
                customer_comments[i] if len(customer_comments) > i else '',
                customer_questions[i] if len(customer_questions) > i else ''
            ])

    return send_file(filename, as_attachment=True, download_name=filename)

if __name__ == '__main__':
    app.run(debug=True)
