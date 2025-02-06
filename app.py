import os
from flask import Flask, render_template, request, redirect, url_for
from datamanager.data_models import db
from datamanager.sqlite_data_manager import SQLiteDataManager


app = Flask(__name__)
data_manager = SQLiteDataManager(db)


def configure_app(app):
    current_directory = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'DATABASE_URI', f'sqlite:///{os.path.join(current_directory, "data", "movieweb_db.sqlite")}'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


def create_database(app, db):
    db.init_app(app)
    with app.app_context():
        db.create_all()


@app.route('/')
def home():
    """Home route"""
    return "Welcome to MovieWeb HEYYApp!"


@app.route('/users')
def list_users():
    pass


@app.route('/users/<int:user_id>')
def list_user_movies(user_id):
    pass


@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    pass


@app.route('/users/<int:user_id>/add_movie', methods=['GET', 'POST'])
def add_movie_to_user(user_id):
    pass


@app.route('/users/<int:user_id>/update_movie/<int:movie_id>', methods=['GET', 'POST'])
def update_movie(movie_id, user_id):
    pass


@app.route('/users/<int:user_id>/remove_movie/<int:movie_id>', methods=['POST'])
def remove_movie_from_user(movie_id, user_id):
    pass


if __name__ == "__main__":
    configure_app(app)

    db_path = os.path.join(os.path.dirname(__file__), "data", "movieweb_db.sqliite")
    if not os.path.exists(db_path):
        create_database(app, db)

    app.run(debug=True)
