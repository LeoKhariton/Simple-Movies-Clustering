import sqlite3
from dash import Dash, dcc, html
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import MultiLabelBinarizer
import plotly.express as px

conn = sqlite3.connect('movies.db')
query = '''
SELECT movies.title, movies.year, movies.rating,
       GROUP_CONCAT(genres.name) AS genres,
       GROUP_CONCAT(directors.name) AS directors
FROM movies
LEFT JOIN movie_genres ON movies.id = movie_genres.movie_id
LEFT JOIN genres ON movie_genres.genre_id = genres.id
LEFT JOIN movie_directors ON movies.id = movie_directors.movie_id
LEFT JOIN directors ON movie_directors.director_id = directors.id
GROUP BY movies.id
'''
data = pd.read_sql_query(query, conn)
conn.close()

# Преобразование категориальных данных в числовые
mlb = MultiLabelBinarizer()
genres_encoded = pd.DataFrame(mlb.fit_transform(data['genres'].str.split(',')), columns=mlb.classes_, index=data.index)
directors_encoded = pd.DataFrame(mlb.fit_transform(data['directors'].str.split(',')), columns=mlb.classes_, index=data.index)

# Объединение данных
data_encoded = pd.concat([data[['year', 'rating']], genres_encoded, directors_encoded], axis=1)

# Кластеризация
kmeans = KMeans(n_clusters=7).fit(data_encoded)

# Добавление результатов кластеризации в исходный DataFrame
data['cluster'] = kmeans.labels_.astype(str)

data_genres = data.assign(genres=data['genres'].str.split(',')).explode('genres').assign(directors=data['directors'].str.split(',')).explode('directors')

# Диаграмма 1: по оси Y - рейтинги, по X - жанры
fig1 = px.scatter(data_genres, x='genres', y='rating', color='cluster', title='Рейтинги по жанрам с кластеризацией', height=700)
# Диаграмма 2: по оси Y - жанры, по X - режиссеры
fig2 = px.scatter(data_genres, x='directors', y='genres', color='cluster', title='Жанры по режиссерам с кластеризацией')
# Диаграмма 3: по оси Y - жанры, по X - года
fig3 = px.scatter(data_genres, x='year', y='genres', color='cluster', title='Жанры по годам с кластеризацией', height=700)
# Диаграмма 4: по оси Y - рейтинги, по X - режиссеры
fig4 = px.scatter(data_genres, x='directors', y='rating', color='cluster', title='Рейтинги по режиссерам с кластеризацией')
# Диаграмма 5: по оси Y - рейтинги, по X - года
fig5 = px.scatter(data, x='year', y='rating', color='cluster', title='Рейтинги по годам с кластеризацией')
# Диаграмма 6: по оси Y - режиссеры, по X - года
fig6 = px.scatter(data_genres, x='year', y='directors', color='cluster', title='Режиссеры по годам с кластеризацией', height=700)
fig7 = px.scatter(data, x='cluster', y='title', color='cluster', title='Кластеризация фильмов', height=700)

app = Dash()

app.layout = html.Div([
    dcc.Graph(figure=fig1),
    dcc.Graph(figure=fig2),
    dcc.Graph(figure=fig3),
    dcc.Graph(figure=fig4),
    dcc.Graph(figure=fig5),
    dcc.Graph(figure=fig6),
    dcc.Graph(figure=fig7)
])

app.run_server(debug=True)