from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField
from wtforms.validators import DataRequired
import requests

TMDB_API_KEY = "12b96c5341abda50dc77bedfa0077028"
MOVIE_DB_INFO_URL = "https://api.themoviedb.org/3/movie"
POSTER_SIZE = "w300"


def get_movie_data(movie_name):
    parameters = {
        "api_key": TMDB_API_KEY,
        "query": movie_name
    }
    search_endpoint = 'https://api.themoviedb.org/3/search/movie'
    response = requests.get(search_endpoint, params=parameters)
    movie_data = response.json()

    return movie_data


def get_movie_details(movie_api_id):
    movie_api_url = f"{MOVIE_DB_INFO_URL}/{movie_api_id}"
    parameters = {
        "api_key": TMDB_API_KEY,
    }
    response = requests.get(movie_api_url, params=parameters)
    data = response.json()
    return data


class EditForm(FlaskForm):
    rating = FloatField('Rating out of 10', validators=[DataRequired()])
    review = StringField('Your review', validators=[DataRequired()])
    done = SubmitField('Done')


class AddForm(FlaskForm):
    title = StringField('Movie Title', validators=[DataRequired()])
    add = SubmitField('Add Movie')


app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'

##CREATE DB
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///movies.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

db.init_app(app)

Bootstrap(app)


##CREATE TABLE
class Movie(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String, nullable=False)
    rating = db.Column(db.Float, nullable=False)
    ranking = db.Column(db.Integer, nullable=False)
    review = db.Column(db.String, nullable=False)
    img_url = db.Column(db.String, nullable=False)


with app.app_context():
    db.create_all()
    # db.session.add(new_movie)
    # db.session.commit()


# new_movie = Movie(
#     title="Phone Booth",
#     year=2002,
#     description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
#     rating=7.3,
#     ranking=10,
#     review="My favourite character was the caller.",
#     img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
# )


@app.route("/")
def home():

    all_movies = Movie.query.order_by(Movie.rating).all()
    # or
    # all_movies = db.session.query(Movie).all()

    # This line loops through all the movies
    for i in range(len(all_movies)):
        # This line gives each movie a new ranking reversed from their order in all_movies
        all_movies[i].ranking = len(all_movies) - i
        db.session.commit()


    return render_template("index.html", all_movies=all_movies)


@app.route('/edit', methods=["GET", "POST"])
def edit():

    form = EditForm()

    movie_id = request.args['id']
    movie_to_edit = Movie.query.get(movie_id)

    if form.validate_on_submit():

        movie_to_edit.rating = request.form['rating']
        movie_to_edit.review = request.form['review']
        db.session.commit()

        return redirect(url_for('home'))

    movie_id = request.args['id']
    print(movie_id)
    movie_selected = Movie.query.get(movie_id)

    return render_template("edit.html", form=form, movie=movie_selected)


@app.route('/delete')
def delete():

    movie_id = request.args['id']
    movie_to_delete = Movie.query.get(movie_id)
    db.session.delete(movie_to_delete)
    db.session.commit()

    return redirect(url_for('home'))


@app.route('/add', methods=["GET", "POST"])
def add():

    form = AddForm()
    if form.validate_on_submit():

        movie_to_add = request.form.get('title')
        search_results = get_movie_data(movie_to_add)

        movies_list = search_results["results"]

        return render_template("select.html", movies_list=movies_list)

    return render_template('add.html', form=form)


@app.route('/select', methods=["GET", "POST"])
def select():

    render_template('select.html')


@app.route('/find')
def find_movie():

    movie_api_id = request.args.get('id')

    if movie_api_id:

        selected_movie = get_movie_details(movie_api_id)

        movie_to_add = Movie(
            title=selected_movie['title'],
            year=selected_movie['release_date'].split('-')[0],
            description=selected_movie['overview'],
            rating=selected_movie['vote_average'],
            review=selected_movie['tagline'],
            img_url=f"https://image.tmdb.org/t/p/{POSTER_SIZE}/{selected_movie['poster_path']}"
        )
        db.session.add(movie_to_add)
        db.session.commit()

        return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
