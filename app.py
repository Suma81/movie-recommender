from flask import Flask, render_template, request
import pickle
import requests
import difflib

app = Flask(__name__)

# load model
movies = pickle.load(open('model/movie_list.pkl','rb'))
similarity = pickle.load(open('model/similarity.pkl','rb'))


# function to fetch movie poster
def fetch_poster(movie_id):
    url = "https://api.themoviedb.org/3/movie/{}?api_key=cea5011be49badcc3f81d432bb53df75&language=en-US".format(movie_id)
    data = requests.get(url)
    data = data.json()
    poster_path = data['poster_path']
    full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
    return full_path


def recommend(movie):

    # find closest movie name
    movie_list = movies['title'].tolist()
    close_matches = difflib.get_close_matches(movie, movie_list)

    if len(close_matches) == 0:
        return ["Movie not found"]*5, [""]*5

    movie = close_matches[0]

    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]

    movies_list = sorted(list(enumerate(distances)),
                         reverse=True,
                         key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_posters = []

    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_posters.append(fetch_poster(movie_id))

    return recommended_movies, recommended_posters

@app.route('/', methods=['GET','POST'])
def index():

    movie_list = movies['title'].values

    if request.method == "POST":

        selected_movie = request.form.get("movie")

        names, posters = recommend(selected_movie)

        return render_template('index.html',
                               movie_list=movie_list,
                               names=names,
                               posters=posters)

    return render_template('index.html', movie_list=movie_list)



def search_movie(query):

    url = f"https://api.themoviedb.org/3/search/movie?api_key=cea5011be49badcc3f81d432bb53df75&query={query}"

    data = requests.get(url).json()

    results = []

    for movie in data['results'][:5]:
        results.append({
            "title": movie['title'],
            "poster": "https://image.tmdb.org/t/p/w500/" + movie['poster_path']
        })

    return results


def latest_movies():

    url = "https://api.themoviedb.org/3/movie/now_playing?api_key=cea5011be49badcc3f81d432bb53df75"

    data = requests.get(url).json()

    movies = []
    posters = []

    for movie in data['results'][:5]:
        movies.append(movie['title'])
        posters.append("https://image.tmdb.org/t/p/w500/" + movie['poster_path'])

    return movies, posters


def get_trending():
    url = "https://api.themoviedb.org/3/trending/movie/day?api_key=cea5011be49badcc3f81d432bb53df75"
    data = requests.get(url).json()

    movies = []
    posters = []

    for movie in data['results'][:5]:
        movies.append(movie['title'])
        posters.append("https://image.tmdb.org/t/p/w500/" + movie['poster_path'])

    return movies, posters

if __name__ == "__main__":
    app.run(debug=True)