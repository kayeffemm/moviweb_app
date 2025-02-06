from sqlalchemy.exc import SQLAlchemyError
from datamanager.data_manager_interface import DataManager
from datamanager.data_models import User, Movie
from omdb_api.omdb_api import request_movie_data


class SQLiteDataManager(DataManager):
    """Manages data persistence using SQLite for users and movies."""
    def __init__(self, db):
        """Initializes the SQLiteDataManager with a SQLAlchemy database session.

        Args:
            db: A SQLAlchemy database session object.
        """
        self.db = db

    def get_all_users(self) -> list:
        """Retrieves all users from the database.

        Returns:
            A list of User objects.  Returns an empty list if no users are found.
            Returns None and logs the error if a SQLAlchemyError occurs.
        """
        try:
            all_users_list = self.db.session.query(User).all()
            return all_users_list

        except SQLAlchemyError as e:
            self.db.session.rollback()
            print(f"Error while retrieving users: {e}")

    def get_user(self, user_id):
        """Retrieves a specific user by ID.

        Args:
            user_id: The ID of the user to retrieve.

        Returns:
            A User object if found, None otherwise. Returns "error" if there is a SQLAlchemyError.
        """
        try:
            user = self.db.session.query(User) \
            .filter(User.id == user_id).first()
            if not user:
                return "error"
            return user

        except SQLAlchemyError as e:
            self.db.session.rollback()
            print(f"Error while fetching User: {e}")

    def get_all_movies(self) -> list:
        """Retrieves all movies from the database.

        Returns:
            A list of Movie objects. Returns an empty list if no movies are found. Returns None if there is a SQLAlchemyError.
        """
        try:
            all_movies_list = self.db.session.query(Movie).all()
            return all_movies_list

        except SQLAlchemyError as e:
            self.db.session.rollback()
            print(f"Error while retrieving movies: {e}")

    def get_user_movies(self, user_id) -> list:
        """Retrieves all movies associated with a specific user.

        Args:
            user_id: The ID of the user.

        Returns:
            A list of Movie objects associated with the user. Raises a ValueError if the user is not found.
            Returns an empty list if the user has no movies.
        """
        user = self.db.session.query(User).get(user_id)
        if not user:
            raise ValueError(f"Theres no User with ID: {user_id}.")
        return user.movies

    def get_movie(self, movie_id):
        """Retrieves a specific movie by ID.

        Args:
            movie_id: The ID of the movie to retrieve.

        Returns:
            A Movie object if found, None otherwise. Returns "error" if there is a SQLAlchemyError.
        """
        try:
            movie = self.db.session.query(Movie) \
            .filter(Movie.id == movie_id).first()
            if not movie:
                return "error"
            return movie

        except SQLAlchemyError as e:
            self.db.session.rollback()
            print(f"Error while fetching movie: {e}")

    def add_user(self, new_username) -> str:
        """Adds a new user to the database.

        Args:
            new_username: The username of the new user.

        Returns:
            A string message confirming user creation.
        Raises:
            TypeError: If new_username is not a string.
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
        """Adds a movie to a user's collection.

        Retrieves movie data from the OMDb API if the movie doesn't exist in the database.

        Args:
            user_id: The ID of the user.
            title: The title of the movie.

        Returns:
            A string message confirming the action.  Returns an error message if there is an error.
        Raises:
            ValueError: If the user is not found.
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
        """Updates movie details for a user.

        Creates a new movie entry to prevent details from being edited for all users.
        If no other user has the old movie in their collection, it is also removed.

        Args:
            user_id: ID of the user whose movie is updated.
            movie_id: ID of the movie to update.
            title: New title (optional).
            director: New director (optional).
            release_year: New release year (optional).
            imdb_rating: New rating (optional).

        Returns:
            A string message confirming the update.
        Raises:
            ValueError: If the movie or user is not found.
            TypeError: If the provided title or director are not strings.
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

    def remove_movie_from_user(self, movie_id, user_id):
        """Removes a movie from a user's collection.

        If the movie is no longer associated with any user, it is also deleted from the database.

        Args:
            movie_id: The ID of the movie to remove.
            user_id: The ID of the user from whose collection the movie is removed.

        Returns:
            A string message confirming the removal.
        Raises:
            ValueError: If the movie or user is not found.
        """
        try:
            movie = self.db.session.query(Movie).get(movie_id)
            if not movie:
                raise ValueError(f"Movie with ID {movie_id} not found.")
            user = self.db.session.query(User).get(user_id)
            if not user:
                raise ValueError(f"User with ID {user_id} not found.")

            if movie in user.movies:
                user.movies.remove(movie)
                self.db.session.commit()
            if len(movie.users) == 0:
                self.db.session.delete(movie)
                self.db.session.commit()
            return f"Successfully removed '{movie.title}' from your list."

        except ValueError as e:
            self.db.session.rollback()
            print(e)
        except SQLAlchemyError as e:
            self.db.session.rollback()
            print(f"Error while removing movie: {e}")

    def delete_movie(self, movie_id, user_id) -> str:
        """Deletes a movie from a user's collection and potentially from the database.

        Removes the movie from the specified user's collection. If no users are left
        associated with the movie, the movie entry is also deleted from the database.

        Args:
            movie_id: The ID of the movie to delete.
            user_id: The ID of the user.

        Returns:
            A string message confirming the removal.
        Raises:
            ValueError: If the movie or user is not found.
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
