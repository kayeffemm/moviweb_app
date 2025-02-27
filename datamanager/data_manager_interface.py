from abc import ABC, abstractmethod

class DataManager(ABC):
    """An interface for data management that enforces a contract for all DataManager implementations."""

    @abstractmethod
    def get_all_users(self):
        """Retrieve all users from the database."""
        pass

    @abstractmethod
    def get_all_movies(self):
        pass

    @abstractmethod
    def get_user_movies(self, user_id):
        """Retrieve all movies associated with a specific user."""
        pass

    @abstractmethod
    def add_user(self, name):
        """Add a new user to the database."""
        pass

    @abstractmethod
    def add_movie_to_user(self, user_id, title):
        """Add a new movie to the database."""
        pass

    @abstractmethod
    def update_movie(self, user_id, movie_id, title=None, director=None, release_year=None, imdb_rating=None):
        """Update details of a specific movie."""
        pass

    @abstractmethod
    def delete_movie(self, movie_id, user_id):
        """Delete a specific movie from the database."""
        pass