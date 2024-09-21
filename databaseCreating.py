import sqlite3
import csv

conn = sqlite3.connect('movies.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS movies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    year INTEGER,
    rating REAL,
    description TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS directors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS genres (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
)
''')

#вспомогательные таблицы для связей "многие-ко-многим"

cursor.execute('''
CREATE TABLE IF NOT EXISTS movie_genres (
    movie_id INTEGER,
    genre_id INTEGER,
    PRIMARY KEY (movie_id, genre_id),
    FOREIGN KEY (movie_id) REFERENCES movies (id),
    FOREIGN KEY (genre_id) REFERENCES genres (id)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS movie_directors (
    movie_id INTEGER,
    director_id INTEGER,
    PRIMARY KEY (movie_id, director_id),
    FOREIGN KEY (movie_id) REFERENCES movies (id),
    FOREIGN KEY (director_id) REFERENCES directors (id)
)
''')

with open("movies.csv", "r", newline='', encoding="utf-8") as csvfile:
    reader = csv.DictReader(csvfile)

    for row in reader:
        cursor.execute('''
        INSERT INTO movies (title, year, rating, description)
        VALUES (?, ?, ?, ?)
        ''', (row['title'], row['year'], row['rating'], row['description']))

        movie_id = cursor.lastrowid

        genres = row['genres'].split(',')
        for genre in genres:
            cursor.execute('SELECT id FROM genres WHERE name = ?', (genre.strip(),))
            genre_id = cursor.fetchone()

            if genre_id is None:
                cursor.execute('INSERT INTO genres (name) VALUES (?)', (genre.strip(),))
                genre_id = cursor.lastrowid
            else:
                genre_id = genre_id[0]

            cursor.execute('INSERT INTO movie_genres (movie_id, genre_id) VALUES (?, ?)', (movie_id, genre_id))

        directors = row['directors'].split(',')
        for director in directors:
            cursor.execute('SELECT id FROM directors WHERE name = ?', (director.strip(),))
            director_id = cursor.fetchone()

            if director_id is None:
                cursor.execute('INSERT INTO directors (name) VALUES (?)', (director.strip(),))
                director_id = cursor.lastrowid
            else:
                director_id = director_id[0]

            cursor.execute('INSERT INTO movie_directors (movie_id, director_id) VALUES (?, ?)', (movie_id, director_id))

conn.commit()
conn.close()

print("База данных успешно создана и заполнена.")