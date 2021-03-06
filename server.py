"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db
from flask import (Flask, render_template, redirect, request, flash,
                   session)
from model import User, Rating, Movie, connect_to_db, db

app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""
    return render_template("homepage.html")


@app.route('/users')
def user_list():
    """Show list of users."""

    users = User.query.all()
    return render_template("user_list.html", users=users)


@app.route('/register', methods=['GET'])
def register_users():
    """Register users by email & password"""

    return render_template("register_form.html")


@app.route('/register', methods=['POST'])
def verify_user():
    """ Check if user is in our db, if not add them """

    email1 = request.form.get('email')
    password = request.form.get('password')

    user = db.session.query(User).filter(User.email == email1).first()

    if not user:
        new_user = User(email=email1, password=password)
        db.session.add(new_user)
        db.session.commit()
        session['logged_in_user'] = new_user.user_id
        flash("Sucessfully registered.")
        return redirect("/")
    else:
        flash("User already exists.")
        return redirect("/log-in")


@app.route('/log-in', methods=['GET'])
def log_in_users():
    """Logging users in by email & password"""

    return render_template("log_in.html")


@app.route('/log-in', methods=['POST'])
def checking_user():
    """Checking user in db and log in"""

    email1 = request.form.get('email')
    password = request.form.get('password')

    user = db.session.query(User).filter(User.email == email1).first()

    if user:
        if password == user.password:
            session['logged_in_user'] = user.user_id
            flash("Logged in")
            return redirect("/")
        else:
            flash("Login failed")
            return redirect("/log-in")
    else:
        flash("You are not yet registered")
        return redirect("/register")


@app.route('/log-out')
def log_out_user():
    """Log out user"""

    session.clear()
    flash("Logged out")
    return redirect("/")


@app.route('/user/<int:user_id>')
def user_info(user_id):
    """Display user age, zipcode Movie list & scores"""

    # user = db.session.query(User).filter(User.user_id == user_id).first()
    user = User.query.get(user_id)

    return render_template("user_info.html", user=user)


@app.route('/movies')
def movie_info():
    """Display movie details."""

    # user = db.session.query(User).filter(User.user_id == user_id).first()
    movies = Movie.query.all()

    return render_template("movie_details.html", movies=movies)


@app.route('/movies/<int:movie_id>')
def movie_ratings(movie_id):
    """Display movie Ratings."""

    # user = db.session.query(User).filter(User.user_id == user_id).first()
    movie = Movie.query.get(movie_id)

    return render_template("movie_ratings.html", movie=movie)


@app.route('/add-rating', methods=['POST'])
def add_rating():
    """Adding rating."""

    movie_id = request.form.get('movie_id')
    new_rating = request.form.get('rating')
    user_id = session.get('logged_in_user')

    rating = Rating.query.filter(Rating.user_id == user_id, Rating.movie_id == movie_id).first()

    if rating:
        rating.score = new_rating
        db.session.commit()
    else:
        rating = Rating(movie_id=movie_id,
                        user_id=user_id,
                        score=new_rating)
        db.session.add(rating)
        db.session.commit()

    return redirect('/movies/' + movie_id)

if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')
