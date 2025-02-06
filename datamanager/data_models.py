from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

# Relational table to avoid a movie being added for each user
movie_user_rel  = db.Table(
    'movie_user_rel',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('movie_id', db.Integer, db.ForeignKey('movies.id'), primary_key=True)
)

class User(db.Model):
    """
    User Table with the following columns:
    - id [PrimaryKey]
    - name
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)

    movies = db.relationship('Movie', secondary=movie_user_rel, back_populates='users')


class Movie(db.Model):
    """
    Movie Table with the following columns:
    - id [PrimaryKey]
    - title
    - director
    - release_year
    - imdb_rating
    - poster_url
    """
    __tablename__ = 'movies'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String, nullable=False)
    director = db.Column(db.String, nullable=False)
    release_year = db.Column(db.Integer, nullable=False)
    imdb_rating = db.Column(db.Float, nullable=False)
    poster_url = db.Column(db.String, nullable=True)

    users = db.relationship('User', secondary=movie_user_rel, back_populates='movies')


if __name__ == "__main__":
    # for testing
    pass