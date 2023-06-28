import psycopg2


conn = psycopg2.connect(
        host="localhost",
        database="searcher",
        user="postgres",
        password="password")


def postgres_query():
    """Create table in Postgres"""
    cur = conn.cursor()

    cur.execute("DROP TABLE IF EXISTS posts;")
    cur.execute("""
        CREATE TABLE posts(
            id SERIAL PRIMARY KEY,
            text TEXT NOT NULL,
            created_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            rubrics TEXT[] NOT NULL
        );
    """)

    conn.commit()


def main():
    postgres_query()


if __name__ == "__main__":
    main()


# conn.commit()

# cur.close()
# conn.close()
