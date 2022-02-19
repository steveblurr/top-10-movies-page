# Top 10 Movies Page
Day-64 of 100 Days of Python

This project leverages Flask, Flask-WTF, Bootstrap (Simple Frontend), SQLAlchemy DB, and it uses the [The Movie Database API](https://developers.themoviedb.org/3/getting-started/introduction) to pull data. 



## Register for an API Key from TMDB 
```python
# The Movie DB - API Information
TMDB_SEARCH_ENDPOINT = "https://api.themoviedb.org/3/search/movie"
TMDB_MOVIE_ID_ENDPOINT = "https://api.themoviedb.org/3/movie/"
TMDB_IMG_URL = "https://image.tmdb.org/t/p/w500"
# Create an environment variable with your API key
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
```
1. `TMDB_SEARCH_ENDPOINT = "https://api.themoviedb.org/3/search/movie"`
  - This is the main endpoint to pull all movies with your search. It will render a page of movies by links. See `select.html` for Jinja template code. 
2. Once you select the movie from the `select.html` page. The next step is to get data for that particular movie by passing the movie.id. 
  - Example: `<a href="{{ url_for('find_movie', id=movie.id) }}">`
  - This will add all the movie that you selected into the SQLAlchemy DB
  ```python
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
  ```
   
  #### NOTE: the `return redirect(url_for('edit_movie', id=movie_entry.id))` will automatically take you to the `edit.html`
  -This is the page that allows you to customize the RATING and REVIEW fields that show up on the home page's movie card with all the details. 
  
  #### Another note: I couldn't figure out how to find the image URL (see `TMDB_IMG_URL = "https://image.tmdb.org/t/p/w500"`) around the TMDB documentation. I will be posting the link for page that does show how to dynamically build your URL so you can render the image from the movie you want to add to your page.  [Configuring URL for Movie Image](https://developers.themoviedb.org/3/configuration/get-api-configuration)
  
  ## Ranking your movie list by the rating you provide
  The best way to rank your movies in your DB by that rating is to query the DB using the 'order_by()' method.
  ```python
  all_movies = Movies.query.order_by(Movies.rating).all()
  ```
  1. Once your DB has been queried, we can run a for loop to organize the rankings of the movies by their ratings.
  ```python
    for i in range(len(all_movies)):
        all_movies[i].ranking = len(all_movies) - i
    db.session.commit()
   ```
  
  The rest of the code is pretty straight forward. I just wanted to point some of the code that I struggled with when working on this project.
   
