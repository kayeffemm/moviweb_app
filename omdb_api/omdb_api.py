import os
from dotenv import load_dotenv
import requests


load_dotenv()
API_KEY = os.getenv("API_KEY")


def request_movie_data(title: str) -> tuple[str, str, str, str, str]|str:
    """
    Fetches movie details from the OMDb API for the given title.

    :param title: The title of the movie to search for.
    :return: A tuple containing (title, director, release year, IMDb rating, poster URL) or an error message.
    """
    try:
        url = f'http://www.omdbapi.com/?apikey={API_KEY}&t={title.strip()}'

        res = requests.get(url)

        if res.status_code == 200:
            movie_details = res.json()

            if movie_details.get('Response') == 'True':
                title = movie_details.get('Title', 'N/A')
                director = movie_details.get('Director', 'N/A')
                year = movie_details.get('Year', 'N/A')
                imdb_rating = movie_details.get('imdbRating', 'N/A')
                poster_url = movie_details.get('Poster', 'N/A')

                return title, director, year, imdb_rating, poster_url
            else:
                return f"Error: {movie_details.get('Error', 'Movie not found!')}"
        else:
            return f"HTTP Error: {res.status_code}"

    except requests.RequestException as e:
        return f"Request Exception: {e}"
