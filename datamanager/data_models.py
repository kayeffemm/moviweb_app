from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Table


class Base(DeclarativeBase):
    pass


class User(Base):
    """
    Table for users with the following columns:
    - id [Primary Key]
    - name
    """
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True, nullable=False, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False)

    movies: Mapped[list["Movie"]] = relationship(secondary="user_movie_association", back_populates="users")


class Movie(Base):
    """
    Table for movies with the following columns:
    - id [Primary Key]
    - title
    - release_year
    - imdb_rating
    - director_id [Foreign key]
    """
    __tablename__ = "movie"
    id: Mapped[int] = mapped_column(primary_key=True, nullable=False, autoincrement=True)
    title: Mapped[str] = mapped_column(nullable=False)
    release_year: Mapped[str] = mapped_column(nullable=False)
    imdb_rating: Mapped[float] = mapped_column(nullable=False)
    director_id: Mapped[int] = mapped_column(ForeignKey("director.id"), nullable=False)

    director: Mapped["Director"] = relationship(back_populates="movies")
    users: Mapped[list["User"]] = relationship(secondary="user_movie_association", back_populates="movies")


class Director(Base):
    """
    Table for directors with the following columns:
    - id [Primary Key]
    - name
    """
    __tablename__ = "director"
    id: Mapped[int] = mapped_column(primary_key=True, nullable=False, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False)

    movies: Mapped[list["Movie"]] = relationship(back_populates="director")


user_movie_association = Table(
    "user_movie_association",
    Base.metadata,
    mapped_column("user_id", ForeignKey("user.id"), primary_key=True),
    mapped_column("movie_id", ForeignKey("movie.id"), primary_key=True)
)