import sqlite3
import dash
from dash import dcc
from dash import html
import plotly.graph_objs as go
import pandas as pd
from sklearn.cluster import KMeans

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
df = pd.read_sql_query(query, conn)
conn.close()

# Convert genres and directors into numerical data using one-hot encoding
df_encoded = pd.get_dummies(df, columns=['genres', 'directors'])

# Select the features for clustering
features = ['year', 'rating'] + list(df_encoded.columns[df_encoded.columns.str.startswith('genres_')]) + list(df_encoded.columns[df_encoded.columns.str.startswith('directors_')])
X = df_encoded[features]

# Perform clustering using K-means
num_clusters = 5  # You can determine the optimal number of clusters using techniques such as the elbow method or silhouette analysis
kmeans = KMeans(n_clusters=num_clusters, random_state=42)
clusters = kmeans.fit_predict(X)

# Add the cluster labels to the DataFrame
df['cluster'] = clusters

# Prepare the bar chart data
cluster_counts = df['cluster'].value_counts().sort_index()
data = [go.Bar(
    x=cluster_counts.index,
    y=cluster_counts.values,
    text=cluster_counts.values,
    textposition='auto',
    name='Number of Movies'
)]

# Create the layout
layout = go.Layout(
    title='Movie Clusters',
    xaxis={'title': 'Cluster'},
    yaxis={'title': 'Number of Movies'}
)

# Define the Dash app and layout
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1('Movie Clusters'),
    dcc.Graph(
        id='cluster-graph',
        figure={
            'data': data,
            'layout': layout
        }
    )
])

# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True)