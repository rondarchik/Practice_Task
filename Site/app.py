from flask import Flask, render_template
import psycopg2


app = Flask(__name__)


def get_db_connection():
    conn = psycopg2.connect(
            host="localhost",
            database="searcher",
            user="postgres",
            password="password")

    return conn


@app.route('/')
def index():  # put application's code here
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute('SELECT * FROM posts')
    posts = cur.fetchall()

    cur.close()
    conn.close()

    return render_template('index.html', posts=posts)


@app.route('/about')
def about():
    return render_template('about.html')


if __name__ == '__main__':
    app.run()
