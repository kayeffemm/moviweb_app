from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from datamanager.data_manager_interface import DataManager

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    movies = relationship("Movie", back_populates="user", cascade="all, delete-orphan")


class Movie(Base):
    __tablename__ = 'movies'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    director = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    rating = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="movies")


class SQLiteDataManager(DataManager):
    """
    SQLite implementation of DataManagerInterface for managing users and movies in a SQLite database.
    """

    def __init__(self, database_url="sqlite:///movieweb.db"):
        self.engine = create_engine(database_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def get_all_users(self):
        """Retrieve all users from the database."""
        session = self.Session()
        users = session.query(User).all()
        session.close()
        return users

    def get_user_movies(self, user_id):
        """Retrieve all movies associated with a specific user."""
        session = self.Session()
        movies = session.query(Movie).filter_by(user_id=user_id).all()
        session.close()
        return movies

    def add_user(self, name):
        """Add a new user to the database."""
        session = self.Session()
        user = User(name=name)
        session.add(user)
        session.commit()
        session.close()

    def add_movie(self, user_id, name, director, year, rating):
        """Add a new movie to the database if it doesn't already exist for the user."""
        session = self.Session()

        existing_movie = session.query(Movie).filter_by(
            user_id=user_id, name=name, director=director, year=year
        ).first()

        if existing_movie:
            session.close()
            print(f"Movie '{name}' by {director} ({year}) already exists for user {user_id}.")
            return

        movie = Movie(user_id=user_id, name=name, director=director, year=year, rating=rating)
        session.add(movie)
        session.commit()
        session.close()

    def update_movie(self, movie_id, name=None, director=None, year=None, rating=None):
        """Update details of a specific movie."""
        session = self.Session()
        movie = session.query(Movie).filter_by(id=movie_id).first()
        if movie:
            if name:
                movie.name = name
            if director:
                movie.director = director
            if year:
                movie.year = year
            if rating:
                movie.rating = rating
            session.commit()
        session.close()

    def delete_movie(self, movie_id):
        """Delete a specific movie from the database."""
        session = self.Session()
        movie = session.query(Movie).filter_by(id=movie_id).first()
        if movie:
            session.delete(movie)
            session.commit()
        session.close()
