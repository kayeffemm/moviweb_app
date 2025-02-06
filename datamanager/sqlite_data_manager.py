from sqlalchemy.exc import SQLAlchemyError
from datamanager.data_manager_interface import DataManager
from datamanager.data_models import User, Movie
from omdb_api.omdb_api import request_movie_data


class SQLiteDataManager(DataManager):
    """
    SQLite Data Manager for CRUD operations on a sqlite file.
    """
    def __init__(self, db):
        """
        Setup SQLiteDataManager with given db
        """
        self.db = db

    def get_all_users(self) -> list:
        """
        List all users from the database.
        :return: list of User objects
        """
        try:
            all_users_list = self.db.session.query(User).all()
            return all_users_list

        except SQLAlchemyError as e:
            self.db.session.rollback()
            print(f"Error while retrieving users: {e}")

    def get_all_movies(self) -> list:
        """
        List all movies from the database
        :return: list of Movie objects
        """
        try:
            all_movies_list = self.db.session.query(Movie).all()
            return all_movies_list

        except SQLAlchemyError as e:
            self.db.session.rollback()
            print(f"Error while retrieving movies: {e}")

    def get_user_movies(self, user_id) -> list:
        """
        List all movies related to given user_id
        :param user_id: ID of the user we want to access
        :return: list of Movie objects related to this user_id
        """
        user = self.db.session.query(User).get(user_id)
        if not user:
            raise ValueError(f"Theres no User with ID: {user_id}.")
        return user.movies

    def add_user(self, new_username) -> str:
        """
        Create User object and add it to the database.
        :param new_username: Name of the user
        :return: None
        """
        if not isinstance(new_username, str):
            raise TypeError(f"Argument name must be string, got {type(new_username)} instead.")

        try:
            new_user = User(name=new_username)
            self.db.session.add(new_user)
            self.db.session.commit()
            return f"{new_username} added as a new user."

        except SQLAlchemyError as e:
            self.db.session.rollback()
            print(f"Error while trying to add a new user to database: {e}")

    def add_movie_to_user(self, user_id, title) -> str:
        """
        TODO: Implement omdb_api support
        Establishes connection between given user_id and movie. If movie does not exist creates Movie object and
        add it to the database.
        :param user_id: ID of the user we want to access
        :param title: movie title
        :return: None
        """
        try:
            user = self.db.session.query(User).get(user_id)
            if not user:
                raise ValueError(f"Theres no User with ID: {user_id}.")

            known_movie = self.db.session.query(Movie).filter(Movie.title == title).first()
            if known_movie:
                if known_movie not in user.movies:
                    user.movies.append(known_movie)
                    self.db.session.commit()
                    return f"{title} added to your list of movies."
                else:
                    return f"{title} already exists in your list of movies."

            res = request_movie_data(title)
            if isinstance(res, tuple) and len(res) == 5:
                fetched_title, fetched_director, fetched_release_year, fetched_imdb_rating, fetched_poster_url = res
            else:
                return "Data is invalid"

            new_movie = Movie(
                title = fetched_title,
                director = fetched_director,
                release_year = fetched_release_year,
                imdb_rating = fetched_imdb_rating,
                poster_url = fetched_poster_url
            )
            user.movies.append(new_movie)
            self.db.session.commit()
            return f"{title} added to your list of movies."

        except ValueError as e:
            self.db.session.rollback()
            print(f"Error: {e}")

        except SQLAlchemyError as e:
            self.db.session.rollback()
            print(f"Error while trying to add a new movie to database: {e}")

    def update_movie(self, user_id, movie_id, title=None, director=None, release_year=None, imdb_rating=None) -> str:
        """
        Used to overwrite existing movie details. Creates a new movie entry to prevent movie details being
        edited for all users. If no other user has the old movie in their collection remove it also.
        :param user_id: ID of user where movie gets updated
        :param movie_id: ID of movie to update
        :param title: New title used for update
        :param director: New director used for update
        :param release_year: New release year used for update
        :param imdb_rating: New imdb_rating used for update
        :return: String, status message
        """
        try:
            movie = self.db.session.query(Movie).get(movie_id)
            user = self.db.session.query(User).get(user_id)

            if not movie:
                raise ValueError(f"There is no movie with id: {movie_id}")
            if not user:
                raise ValueError(f"There is no user with id: {user_id}")

            new_title = title
            new_director = director
            try:
                new_release_year = int(release_year)
            except ValueError as e:
                print(f"Error: {e}")
                new_release_year = movie.release_year
            try:
                new_rating = float(imdb_rating)
            except ValueError as e:
                print(f"Error: {e}")
                new_rating = movie.imdb_rating

            if not isinstance(new_title, str):
                raise TypeError(f"Expected string for title, got {type(new_title)} instead.")
            if not isinstance(new_director, str):
                raise TypeError(f"Expected string for director, got {type(new_director)} instead.")

            self.delete_movie(movie_id, user_id)
            new_movie = Movie(
                title = new_title,
                director = new_director,
                release_year = new_release_year,
                imdb_rating = new_rating,
                poster_url = movie.poster_url
            )
            user.movies.append(new_movie)
            self.db.session.commit()
            return f"{movie.title} updated!"

        except ValueError as e:
            self.db.session.rollback()
            print(e)

        except TypeError as e:
            self.db.session.rollback()
            print(e)

        except SQLAlchemyError as e:
            self.db.session.rollback()
            print(e)

    def delete_movie(self, movie_id, user_id) -> str:
        """
        Delete a movie from user_id collection. If no user left with movie -> also delete the movie from database.
        :param movie_id: Integer, id of movie to delete
        :param user_id: Integer, id of user
        :return: String, status message.
        """
        try:
            movie = self.db.session.query(Movie).get(movie_id)
            user = self.db.session.query(User).get(user_id)

            if not movie:
                raise ValueError(f"There is no movie with id: {movie_id}")
            if not user:
                raise ValueError(f"There is no user with id: {user_id}")

            if movie in user.movies:
                user.movies.remove(movie)
                self.db.session.commit()

            if not movie.users:
                self.db.session.delete(movie)
                self.db.session.commit()

            return f"{movie} has been removed from your list."

        except ValueError as e:
            self.db.session.rollback()
            print(e)

        except SQLAlchemyError as e:
            self.db.session.rollback()
            print(f"Error while trying to remove movie from database: {e}")
