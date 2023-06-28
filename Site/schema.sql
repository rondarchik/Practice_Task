DROP IF EXISTS TABLE Posts;

CREATE TABLE Posts (
  id SERIAL PRIMARY KEY,
  text TEXT NOT NULL,
  created_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  rubrics TEXT[] NOT NULL
);

grant all privileges on database searcher to postgres;
grant all privileges on all tables in schema public to postgres;
grant all privileges on all sequences in schema public to postgres;
grant all privileges on all functions in schema public to postgres;
