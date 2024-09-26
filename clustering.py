import sqlite3
from dash import Dash, dcc, html, Input, Output, callback
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import LabelEncoder
import plotly.express as px

conn = sqlite3.connect('movies.db')
query = '''
SELECT movies.title, movies.year, movies.rating,
       genres.name AS genre,
       directors.name AS director
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
le = LabelEncoder()
genre_encoded = le.fit_transform(data['genre'])
director_encoded = le.fit_transform(data['director'])

# Объединение данных
data_encoded = pd.DataFrame({
    'year': data['year'],
    'rating': data['rating'],
    'genre': genre_encoded,
    'director': director_encoded
})

# Кластеризация
kmeans = KMeans(n_clusters=7).fit_predict(data_encoded)

data['cluster'] = kmeans.astype(str)


app = Dash()

app.layout = html.Div([
    dcc.Dropdown(
        id='x-axis',
        options=[
            {'label': 'Названия', 'value': 'title'},
            {'label': 'Рейтинги', 'value': 'rating'},
            {'label': 'Жанры', 'value': 'genre'},
            {'label': 'Режиссеры', 'value': 'director'},
            {'label': 'Года', 'value': 'year'},
            {'label': 'Кластеры', 'value': 'cluster'}
        ],
        value='year'
    ),
    dcc.Dropdown(
        id='y-axis',
        options=[
            {'label': 'Названия', 'value': 'title'},
            {'label': 'Рейтинги', 'value': 'rating'},
            {'label': 'Жанры', 'value': 'genre'},
            {'label': 'Режиссеры', 'value': 'director'},
            {'label': 'Года', 'value': 'year'},
            {'label': 'Кластеры', 'value': 'cluster'}
        ],
        value='title'
    ),
    dcc.Graph(id='scatter-plot'),

    dcc.Dropdown(
        id='x-axis-3d',
        options=[
            {'label': 'Названия', 'value': 'title'},
            {'label': 'Рейтинги', 'value': 'rating'},
            {'label': 'Жанры', 'value': 'genre'},
            {'label': 'Режиссеры', 'value': 'director'},
            {'label': 'Года', 'value': 'year'},
            {'label': 'Кластеры', 'value': 'cluster'}
        ],
        value='year'
    ),
    dcc.Dropdown(
        id='y-axis-3d',
        options=[
            {'label': 'Названия', 'value': 'title'},
            {'label': 'Рейтинги', 'value': 'rating'},
            {'label': 'Жанры', 'value': 'genre'},
            {'label': 'Режиссеры', 'value': 'director'},
            {'label': 'Года', 'value': 'year'},
            {'label': 'Кластеры', 'value': 'cluster'}
        ],
        value='genre'
    ),
    dcc.Dropdown(
        id='z-axis-3d',
        options=[
            {'label': 'Названия', 'value': 'title'},
            {'label': 'Рейтинги', 'value': 'rating'},
            {'label': 'Жанры', 'value': 'genre'},
            {'label': 'Режиссеры', 'value': 'director'},
            {'label': 'Года', 'value': 'year'},
            {'label': 'Кластеры', 'value': 'cluster'}
        ],
        value='rating'
    ),
    dcc.Graph(id='scatter-plot-3d')
])

@callback(
    Output('scatter-plot', 'figure'),
    [Input('x-axis', 'value'),
     Input('y-axis', 'value')]
)
def update_graph(x_axis, y_axis):
    fig = px.scatter(data, x=x_axis, y=y_axis, color='cluster', title=f'Кластеризация фильмов', height=700, hover_data=['title', 'year', 'rating', 'genre', 'director', 'cluster'])
    return fig

@callback(
     Output('scatter-plot-3d', 'figure'),
    [Input('x-axis-3d', 'value'),
     Input('y-axis-3d', 'value'),
     Input('z-axis-3d', 'value')]
)
def update_graph3d(x_axis3d, y_axis3d, z_axis3d):
    fig = px.scatter_3d(data, x=x_axis3d, y=y_axis3d, z=z_axis3d, color='cluster', title=f'Кластеризация фильмов', height=1000, hover_data=['title', 'year', 'rating', 'genre', 'director', 'cluster'])
    return fig

app.run_server(debug=True)