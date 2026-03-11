import pandas as pd
import numpy as np
import ast
import pickle

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# load datasets
movies = pd.read_csv('data/movies.csv')
credits = pd.read_csv('data/credits.csv')

# merge datasets
movies = movies.merge(credits, on='title')

movies = movies[['movie_id','title','overview','genres','keywords','cast','crew']]

movies.dropna(inplace=True)

# convert string to list
def convert(obj):
    L = []
    for i in ast.literal_eval(obj):
        L.append(i['name'])
    return L

movies['genres'] = movies['genres'].apply(convert)
movies['keywords'] = movies['keywords'].apply(convert)

# fetch top 3 cast
def convert_cast(obj):
    L=[]
    counter=0
    for i in ast.literal_eval(obj):
        if counter!=3:
            L.append(i['name'])
            counter+=1
        else:
            break
    return L

movies['cast'] = movies['cast'].apply(convert_cast)

# fetch director
def fetch_director(obj):
    L=[]
    for i in ast.literal_eval(obj):
        if i['job']=='Director':
            L.append(i['name'])
            break
    return L

movies['crew'] = movies['crew'].apply(fetch_director)

# split overview
movies['overview'] = movies['overview'].apply(lambda x:x.split())

# create tags
movies['tags'] = movies['overview'] + movies['genres'] + movies['keywords'] + movies['cast'] + movies['crew']

new_df = movies[['movie_id','title','tags']]

# convert list to string
new_df['tags'] = new_df['tags'].apply(lambda x:" ".join(x))

# vectorization
cv = CountVectorizer(max_features=5000,stop_words='english')
vectors = cv.fit_transform(new_df['tags']).toarray()

# similarity matrix
similarity = cosine_similarity(vectors)

# save model
pickle.dump(new_df, open('model/movie_list.pkl','wb'))
pickle.dump(similarity, open('model/similarity.pkl','wb'))

print("Model created successfully!")