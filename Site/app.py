import json

from flask import Flask, render_template, request
import elasticsearch
import psycopg2


with open("config.json", "r") as file:
    config = json.load(file)

es = elasticsearch.Elasticsearch(
    hosts=["http://127.0.0.1:9200"],
    basic_auth=(config['elasticsearch']['user'], config['elasticsearch']['password'])
)
INDEX_NAME = 'posts'


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


@app.route('/search', methods=['POST'])
def search():
    text = request.form['search']

    body = {
        "size": 20,
        "query": {
            "span_multi": {
                "match": {
                    "fuzzy": {
                        "text": {
                            "value": text,
                            "fuzziness": "AUTO"
                        }
                    }
                }
            }
        }
    }

    data = es.search(index=INDEX_NAME, body=body)
    id_lists = []
    for item in data["hits"]["hits"]:
        id_lists.append(item["_source"]["id"])

    conn = get_db_connection()
    cur = conn.cursor()

    if id_lists:
        query = "SELECT text, created_date, rubrics FROM posts WHERE id IN (%s)" % (', '.join(str(id) for id in id_lists))
        query += " ORDER BY created_date;"

        cur.execute(query)
        posts = cur.fetchall()
    else:
        posts = ''

    cur.close()
    conn.close()

    return render_template('search.html', posts=posts)


if __name__ == '__main__':
    app.run()
