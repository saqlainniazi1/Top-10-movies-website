import requests

TMDB_API_KEY = "12b96334328"
MOVIE_DB_INFO_URL = "https://api.themoviedb.org/3/movie"

# def get_movie_data(movie_name):
#
#     parameters = {
#         "api_key" : TMDB_API_KEY,
#         "query" : movie_name
#     }
#
#     search_endpoint = 'https://api.themoviedb.org/3/search/movie'
#     response = requests.get(search_endpoint, params=parameters)
#
#     movie_data = response.json()
#
#     return movie_data
#
#
# data = get_movie_data("Fight Club")
# print(data)


def get_movie_details(movie_api_id):
    movie_api_url = f"{MOVIE_DB_INFO_URL}/{movie_api_id}"
    parameters = {
        "api_key": TMDB_API_KEY,
    }
    response = requests.get(movie_api_url, params=parameters)
    data = response.json()
    print(data)


get_movie_details(100)

