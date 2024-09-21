import sqlite3
import dash
from dash import dcc, html
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import MultiLabelBinarizer, MinMaxScaler, StandardScaler, MultiLabelBinarizer, OneHotEncoder, LabelEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import plotly.express as px
import plotly.graph_objs as go

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

data['genres'] = data['genres'].str.split(',')
data['directors'] = data['directors'].str.split(',')

mlb_genres = MultiLabelBinarizer()
mlb_directors = MultiLabelBinarizer()
genres_binary = mlb_genres.fit_transform(data['genres'])
directors_binary = mlb_directors.fit_transform(data['directors'])

genres_df = pd.DataFrame(genres_binary, columns=mlb_genres.classes_)
directors_df = pd.DataFrame(directors_binary, columns=mlb_directors.classes_)

data = pd.concat([data, genres_df, directors_df], axis=1)

data.drop(['genres', 'directors'], axis=1, inplace=True)

preprocessor = ColumnTransformer(
    transformers=[
        ('year_rating', MinMaxScaler(), ['year', 'rating'])
    ])

preprocessed_data = preprocessor.fit_transform(data)

kmeans = KMeans(n_clusters=5)
clusters = kmeans.fit_predict(preprocessed_data)

data['cluster'] = clusters



app = dash.Dash(__name__)

figures = []
for genre in data['genres'].unique():
    fig = px.box(data[data['genres'] == genre], x='genres', y='rating', color='cluster')
    figures.append(fig)

# Define the layout of the Dash application
app.layout = html.Div(children=[
    html.H1(children='Movie Clustering'),

    html.Div(children='''
        Box plots of ratings for each genre
    '''),
    html.Div(children=[
        dcc.Graph(
            id=f'box-plot-{i}',
            figure=fig
        )
        for i, fig in enumerate(figures)
    ])
])

if __name__ == '__main__':
    app.run_server(debug=True)