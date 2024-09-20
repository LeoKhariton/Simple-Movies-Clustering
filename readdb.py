import sqlite3
import dash
from dash import dcc
from dash import html
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import MultiLabelBinarizer, MinMaxScaler
from dash.dependencies import Input, Output
import plotly.express as px
import numpy as np
from sklearn.preprocessing import StandardScaler, MultiLabelBinarizer
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

# Step 2: Preprocess the data
# Encode categorical variables
mlb = MultiLabelBinarizer()
genres_encoded = mlb.fit_transform(data['genres'].str.split(','))
directors_encoded = mlb.fit_transform(data['directors'].str.split(','))

# Scale numerical variables
scaler = StandardScaler()
year_rating_scaled = scaler.fit_transform(data[['year', 'rating']])

# Combine the encoded and scaled variables
X = np.hstack((genres_encoded, directors_encoded, year_rating_scaled))

# Step 3: Apply K-means clustering
kmeans = KMeans(n_clusters=5, random_state=42)
clusters = kmeans.fit_predict(X)

# Step 4: Create a Dash app for visualization
app = dash.Dash(__name__)

# Create a scatter plot of the clusters
trace = go.Scatter(
    x=data['year'],
    y=data['rating'],
    mode='markers',
    marker=dict(color=clusters),
    text=data['title']
)

layout = go.Layout(
    title='Movie Clusters',
    xaxis=dict(title='Year'),
    yaxis=dict(title='Rating')
)

fig = go.Figure(data=[trace], layout=layout)

app.layout = html.Div([
    dcc.Graph(id='cluster-plot', figure=fig)
])

# Step 5: Add a smooth animation to the visualization
# You can use the `animate` function from the `plotly.express` module to add animation to the scatter plot
# Refer to the Plotly documentation for more details on how to use the `animate` function

# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True)