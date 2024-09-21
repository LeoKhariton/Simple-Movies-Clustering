import sqlite3
import dash
from dash import dcc, html
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
kmeans = KMeans(n_clusters=5).fit(data_encoded)

# Добавление результатов кластеризации в исходный DataFrame
data['cluster'] = kmeans.labels_


app = dash.Dash(__name__)

# Диаграмма 1: по оси Y - рейтинги, по X - жанры
fig1 = px.scatter(data, x='genres', y='rating', color='cluster', title='Рейтинги по жанрам с кластеризацией')

# Диаграмма 2: по оси Y - жанры, по X - режиссеры
fig2 = px.scatter(data, x='directors', y='genres', color='cluster', title='Жанры по режиссерам с кластеризацией')

# Диаграмма 3: по оси Y - жанры, по X - года
fig3 = px.scatter(data, x='year', y='genres', color='cluster', title='Жанры по годам с кластеризацией')

# Диаграмма 4: по оси Y - рейтинги, по X - режиссеры
fig4 = px.scatter(data, x='directors', y='rating', color='cluster', title='Рейтинги по режиссерам с кластеризацией')

# Диаграмма 5: по оси Y - рейтинги, по X - года
fig5 = px.scatter(data, x='year', y='rating', color='cluster', title='Рейтинги по годам с кластеризацией')

# Диаграмма 6: по оси Y - режиссеры, по X - года
fig6 = px.scatter(data, x='year', y='directors', color='cluster', title='Режиссеры по годам с кластеризацией')

app.layout = html.Div(children=[
    dcc.Graph(
        id='graph1',
        figure=fig1
    ),
    dcc.Graph(
        id='graph2',
        figure=fig2
    ),
    dcc.Graph(
        id='graph3',
        figure=fig3
    ),
    dcc.Graph(
        id='graph4',
        figure=fig4
    ),
    dcc.Graph(
        id='graph5',
        figure=fig5
    ),
    dcc.Graph(
        id='graph6',
        figure=fig6
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)