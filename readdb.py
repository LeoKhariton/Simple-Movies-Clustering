import sqlite3
import dash
from dash import dcc
from dash import html
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import MultiLabelBinarizer, MinMaxScaler
from dash.dependencies import Input, Output
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

# Step 2: Preprocess the data
# Encode genres and directors using MultiLabelBinarizer
mlb_genres = MultiLabelBinarizer()
genres_encoded = mlb_genres.fit_transform(data['genres'].str.split(','))
genres_df = pd.DataFrame(genres_encoded, columns=mlb_genres.classes_)

mlb_directors = MultiLabelBinarizer()
directors_encoded = mlb_directors.fit_transform(data['directors'].str.split(','))
directors_df = pd.DataFrame(directors_encoded, columns=mlb_directors.classes_)

# Scale year and rating using MinMaxScaler
scaler = MinMaxScaler()
year_rating_scaled = scaler.fit_transform(data[['year', 'rating']])
year_rating_df = pd.DataFrame(year_rating_scaled, columns=['year_scaled', 'rating_scaled'])

# Combine the encoded and scaled features
processed_data = pd.concat([data[['title']], genres_df, directors_df, year_rating_df], axis=1)

# Step 3: Perform K-means clustering
kmeans = KMeans(n_clusters=5, random_state=42)
clusters = kmeans.fit_predict(processed_data.drop('title', axis=1))

# Step 4: Visualize the clusters using Dash
app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.Graph(id='cluster-graph')
])

@app.callback(
    Output('cluster-graph', 'figure'),
    [Input('cluster-graph', 'id')]
)
def update_graph(input_value):
    fig = px.scatter(processed_data, x='year_scaled', y='rating_scaled', color=clusters, hover_data=['title'])
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)