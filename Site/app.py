import json

from flask import Flask, render_template, request, redirect, flash, url_for
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
        query = "SELECT text, created_date, rubrics FROM posts WHERE id IN (%s)"%(', '.join(str(id) for id in id_lists))
        query += " ORDER BY created_date;"

        cur.execute(query)
        posts = cur.fetchall()
    else:
        posts = ''

    cur.close()
    conn.close()

    return render_template('search.html', posts=posts)


def search_by_id(id):
    body = {
        "size": 1,
        "query": {
            "match": {
                "id": id
            }
        }
    }

    result = es.search(index=INDEX_NAME, body=body)["hits"]["hits"]

    if len(result) == 0:
        return None

    return result


def delete_by_id(id):
    try:
        es.delete(index=INDEX_NAME, id=id)
        return True
    except elasticsearch.exceptions.NotFoundError:
        return False


@app.route('/delete', methods=['POST'])
def delete():
    conn = get_db_connection()
    cur = conn.cursor()

    id = request.form['id']
    delete_post = search_by_id(id)

    if delete_post:
        delete_by_id(delete_post[0]['_id'])
        cur.execute("DELETE FROM posts WHERE id=%s", (id))

    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run()
