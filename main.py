from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
import os
import requests


app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///top_ten_movies.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
Bootstrap(app)
db = SQLAlchemy(app)

# The Movie DB - API Information
TMDB_SEARCH_ENDPOINT = "https://api.themoviedb.org/3/search/movie"
TMDB_MOVIE_ID_ENDPOINT = "https://api.themoviedb.org/3/movie/"
TMDB_IMG_URL = "https://image.tmdb.org/t/p/w500"
TMDB_API_KEY = os.getenv("TMDB_API_KEY")


class Movies(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), unique=True, nullable=False)
    year = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    rating = db.Column(db.Float, nullable=True)
    ranking = db.Column(db.Integer, nullable=True)
    review = db.Column(db.String(255), nullable=True)
    img_url = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f'<Movies  {self.title}>'


class EditForm(FlaskForm):
    new_rating = FloatField('New Rating:', validators=[DataRequired()])
    new_review = StringField('Your Review:')
    submit = SubmitField('Submit')


class AddForm(FlaskForm):
    search_movie = StringField('Movie Title', validators=[DataRequired()])
    submit = SubmitField('Submit')


@app.route("/")
def home():
    all_movies = Movies.query.order_by(Movies.rating).all()

    for i in range(len(all_movies)):
        all_movies[i].ranking = len(all_movies) - i
    db.session.commit()

    return render_template("index.html", movies=all_movies)


@app.route("/add", methods=['GET', 'POST'])
def add_movie():
    form = AddForm()
    if form.validate_on_submit() and request.method == "POST":
        movie_entry = form.search_movie.data
        response = requests.get(TMDB_SEARCH_ENDPOINT, params={'api_key': TMDB_API_KEY, 'query': movie_entry})
        response.raise_for_status()
        data = response.json()['results']
        # print(data)
        return render_template('select.html', data=data)

    return render_template('add.html', form=form)


@app.route("/find", methods=['GET', 'POST'])
def find_movie():
    movie_id = request.args.get('id')
    response = requests.get(url=f'{TMDB_MOVIE_ID_ENDPOINT}/{movie_id}', params={'api_key': TMDB_API_KEY,
                                                                            'language': 'en-US'})
    data = response.json()

    movie_entry = Movies(title=data['original_title'],
                         year=data['release_date'].split("-")[0],
                         description=data['overview'],
                         rating=0.0,
                         ranking=0,
                         review="Enter Review Here",
                         img_url=f'{TMDB_IMG_URL}{data["poster_path"]}')
    db.session.add(movie_entry)
    db.session.commit()
    return redirect(url_for('edit_movie', id=movie_entry.id))


@app.route("/edit", methods=['GET', 'POST'])
def edit_movie():
    edit_form = EditForm()

    movie_id = request.args.get('id')
    movie_query = Movies.query.get(movie_id)

    if edit_form.validate_on_submit():
        movie_query.rating = float(edit_form.new_rating.data)
        movie_query.review = edit_form.new_review.data
        db.session.commit()

        return redirect(url_for('home'))

    return render_template('edit.html', form=edit_form, movie=movie_query)


@app.route("/delete", methods=['GET', 'POST'])
def delete_movie():
    movie_id = request.args.get('id')
    movie_query = Movies.query.get(movie_id)
    db.session.delete(movie_query)
    db.session.commit()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
    db.create_all()
