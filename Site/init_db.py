import csv
import json
import pandas
import psycopg2
import elasticsearch


conn = psycopg2.connect(
        host="localhost",
        database="searcher",
        user="postgres",
        password="password")


with open("config.json", "r") as file:
    config = json.load(file)

es = elasticsearch.Elasticsearch(
    hosts=["http://127.0.0.1:9200"],
    basic_auth=(config['elasticsearch']['user'], config['elasticsearch']['password'])
)
INDEX_NAME = 'posts'


def insert_to_elastic():
    body = {
        'mappings': {
            'properties': {
                'id': {'type': 'integer'},
                'text': {'type': 'text'}
            }
        }
    }
    es.indices.delete(index=INDEX_NAME)
    es.indices.create(index=INDEX_NAME, body=body)

    cur = conn.cursor()
    cur.execute("SELECT id, text FROM posts;")

    for row in cur.fetchall():
        id = row[0]
        text = row[1]

        body = {
            'id': id,
            'text': text
        }
        es.index(index=INDEX_NAME, body=body)


def insert_to_postgres():
    cur = conn.cursor()
    cur.execute("set client_encoding='UTF-8';")

    cur.execute("DROP TABLE IF EXISTS posts;")
    cur.execute("""
        CREATE TABLE posts(
            id SERIAL PRIMARY KEY,
            text TEXT NOT NULL,
            created_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            rubrics TEXT[] NOT NULL
        );
    """)

    with open('posts.csv', 'r', encoding="utf-8") as file:
        reader = csv.reader(file)
        next(reader)

        for row in reader:
            query = u'INSERT INTO posts (text, created_date, rubrics) VALUES  (%s, %s, %s);'
            cur.execute(query, (row[0], row[1], row[2]))

    conn.commit()
    print('successfully')


def main():
    insert_to_postgres()
    insert_to_elastic()


if __name__ == "__main__":
    main()

