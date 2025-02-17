import os
from flask import Flask, render_template, request, redirect, url_for
from datamanager.data_models import db
from datamanager.sqlite_data_manager import SQLiteDataManager


app = Flask(__name__)
data_manager = SQLiteDataManager(db)


def configure_app(app):
    """Configures the Flask application.

    Sets the database URI based on the DATABASE_URI environment variable or
    defaults to a SQLite database file in the 'data' directory.  Disables
    SQLAlchemy's modification tracking.

    Args:
        app: The Flask application instance.
    """
    current_directory = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'DATABASE_URI', f'sqlite:///{os.path.join(current_directory, "data", "movieweb_db.sqlite")}'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)


def create_database(app, db):
    """Creates the database tables if they don't exist.

    Initializes the database connection with the Flask app context and then
    creates all defined database tables.

    Args:
        app: The Flask application instance.
        db: The SQLAlchemy database object.
    """
    db.init_app(app)
    with app.app_context():
        db.create_all()


@app.route('/')
def home():
    """Renders the home page.

    Returns:
        A tuple containing the rendered 'home.html' template and a 200 status code.
    """
    return render_template('home.html'), 200


@app.route('/users')
def list_users():
    """Lists all users.

    Retrieves all users from the database and renders the 'users.html' template,
    passing the user data.

    Returns:
        A tuple containing the rendered 'users.html' template and a 200 status code.
    """
    users = data_manager.get_all_users()
    return render_template('users.html', users=users), 200


@app.route('/users/<int:user_id>')
def list_user_movies(user_id):
    """Lists movies for a specific user.

    Retrieves the movies associated with the given user ID and renders the
    'user_movies.html' template.  Handles cases where the user is not found.

    Args:
        user_id: The ID of the user.

    Returns:
        A tuple containing the rendered 'user_movies.html' template and a 200 status code,
        or a tuple containing the '404.html' template and a 404 status code if the user is not found.
    """
    user = data_manager.get_user(user_id)
    action_result = request.args.get('action_result')
    user_movies = data_manager.get_user_movies(user_id)
    if user_movies == "error":
        return render_template('404.html'), 404
    return render_template('user_movies.html', user_movies=user_movies, user=user, user_id=user_id,
                           action_result=action_result), 200


@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    """Handles adding a new user.

    GET requests render the 'add_user.html' form.
    POST requests process the submitted form data, add the user to the database,
    and redirect to the home page with a success message. Handles duplicate usernames.

    Returns:
        A tuple containing the rendered template and status code.
    """
    if request.method == 'GET':
        return render_template('add_user.html'), 200

    if request.method == 'POST':
        username = request.form['username']
        new_user = data_manager.add_user(username)
        if new_user:
            return render_template('add_user.html', user_used=new_user), 200
        success_message = f"User '{username}' has successfully been created."
        return render_template('home.html', success_message=success_message), 201


@app.route('/users/<int:user_id>/add_movie', methods=['GET', 'POST'])
def add_movie_to_user(user_id):
    """Handles adding a movie to a user.

    GET requests render the 'add_movie.html' form.
    POST requests process the submitted form data, add the movie to the user,
    and redirect to the user's movie list.

    Args:
        user_id: The ID of the user.

    Returns:
        A redirect to the user's movie list.
    """
    if request.method == 'GET':
        return render_template('add_movie.html', user_id=user_id), 200

    if request.method == 'POST':
        movie_name = request.form['movie_name']
        action_result = data_manager.add_movie_to_user(user_id, movie_name)
        return redirect(url_for('list_user_movies', action_result=action_result, user_id=user_id))


@app.route('/users/<int:user_id>/update_movie/<int:movie_id>', methods=['GET', 'POST'])
def update_movie(movie_id, user_id):
    """Handles updating a movie.

    GET requests render the 'update_movie.html' form, pre-filled with the
    current movie details. POST requests process the submitted form data,
    update the movie, and redirect to the user's movie list. Handles cases where the movie or user is not found.

    Args:
        movie_id: The ID of the movie to update.
        user_id: The ID of the user who owns the movie.

    Returns:
       A tuple containing the rendered 'update_movie.html' template and a 200 status code on GET,
       or a redirect to the user's movie list on POST. Returns a 404 status code if the user or movie is not found.
    """
    if request.method == 'GET':
        user = data_manager.get_user(user_id)
        movie = data_manager.get_movie(movie_id)
        if user == "error" or movie == "error":
            return render_template('404.html'), 404

        return render_template('update_movie.html', user=user, movie=movie)

    if request.method == 'POST':
        new_title = request.form['title']
        new_director = request.form['director']
        new_publication_year = request.form['publication_year']
        new_rating = request.form['rating']
        action_result = data_manager.update_movie(user_id, movie_id, new_title, new_director, new_publication_year, new_rating)
        return redirect(url_for('list_user_movies', action_result=action_result, user_id=user_id))


@app.route('/users/<int:user_id>/remove_movie/<int:movie_id>', methods=['POST'])
def remove_movie_from_user(movie_id, user_id):
    """Handles removing a movie from a user.

    POST requests remove the movie and redirect to the user's movie list.

    Args:
        movie_id: The ID of the movie to remove.
        user_id: The ID of the user.

    Returns:
        A redirect to the user's movie list.
    """
    action_result = data_manager.remove_movie_from_user(movie_id, user_id)
    return redirect(url_for('list_user_movies', action_result=action_result, user_id=user_id))


@app.errorhandler(400)
def internal_server_error(e):
    """Handles 400 Bad Request errors."""
    return render_template('400.html', e=e), 400


@app.errorhandler(404)
def page_not_found(e):
    """Handles 404 Page Not Found errors."""
    return render_template('404.html', e=e), 404


@app.errorhandler(500)
def internal_server_error(e):
    """Handles 500 Internal Server Error errors."""
    return render_template('500.html', e=e), 500


if __name__ == "__main__":
    configure_app(app)

    #db_path = os.path.join(os.path.dirname(__file__), "data", "movieweb_db.sqlite")
    #if not os.path.exists(db_path):
    #    create_database(app, db)

    app.run(host="0.0.0.0", port=5000, debug=True)
