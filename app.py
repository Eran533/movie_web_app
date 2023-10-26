import ssl
from flask import Flask, render_template, request, redirect, url_for
from movie_web_app.data_models import db
from movie_web_app.datamanager.SQLiteDataManager import SQLiteDataManager
import os
from email.message import EmailMessage
import smtplib
from movie_web_app.api import api
from movie_web_app.game import TriviaGame
import requests

app = Flask(__name__)
db_path = os.path.join(os.path.dirname(__file__), "datamanager", "moviwebapp.db")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
data_manager = SQLiteDataManager(app)
app.register_blueprint(api, url_prefix='/api')
game = TriviaGame()

def send_email(email):
    email_sender = "movieapp533@gmail.com"
    email_password = "kqajiawvooxmuasl"
    email_reciver = email
    subject = "Welcome to the movies app!"
    body = """
    Welcome to the movies application, you are welcome to start discovering the wonderful world of movies!
    """
    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = email_reciver
    em['Subject'] = subject
    em.set_content(body)
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email_reciver, em.as_string())

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

def api(movie_name):
    """
        Calls the OMDB API to retrieve movie information based on the given movie name.

        Args:
            movie_name (str): The name of the movie to search for.

        Returns:
            dict: Movie information retrieved from the OMDB API.
        """
    api_key = "26e330a6&t"
    name_movie = movie_name
    url = f"https://www.omdbapi.com/?apikey={api_key}={name_movie}"
    res = requests.get(url)
    res = res.json()
    return res

def country_flag(country_name):
    """
       Retrieves the flag image URL for a given country name.

       Args:
           country_name (str): The name of the country.

       Returns:
           str: The URL of the country's flag image.
       """
    url = f"https://cdn.jsdelivr.net/npm/country-flag-emoji-json@2.0.0/dist/index.json"
    res = requests.get(url)
    res = res.json()
    image = ''
    for country in res:
        if country["name"] == country_name:
            image = country["image"]
    return image

def app_review(movie_title):
    url = "https://chatgpt-best-price.p.rapidapi.com/v1/chat/completions"

    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {
                "role": "user",
                "content": f"What is your opinion about the film (act like you Film critic)?{movie_title}",
            }
        ]
    }
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": "d73f442011msh63871ecf2dde8bap143fadjsne460c0fb111c",
        "X-RapidAPI-Host": "chatgpt-best-price.p.rapidapi.com"
    }

    response = requests.post(url, json=payload, headers=headers)
    review_text = response.json()['choices'][0]['message']['content']
    return review_text

@app.route('/', methods=['GET', 'POST'])
def home():
    try:
        users = data_manager.get_all_users()
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            email = request.form.get('email')
            image = request.files.get('image')
            confirm_password = request.form.get('confirm_password')
            if password != confirm_password:
                return render_template("index.html", error_message="Passwords do not match")
            if any(account["username"].lower() == username.lower() or account["email"].lower() == email.lower() for
                   account in users):
                return render_template("index.html", error_message="Username/Email already exists")
            new_id = 1 if not users else max(account['id'] for account in users) + 1
            image_filename = f'{username}.png'
            if image:
                try:
                    image.save(f'static/{image_filename}')
                except:
                    return render_template("index.html", error_message="Failed to save the image file")
            new_account = {
                "id": new_id,
                "username": username,
                "email": email,
                "password": password,
                "image": image_filename,
                "movies": []
            }
            data_manager.add_user(new_account)
            send_email(email)
            return redirect(url_for('log_in'))
        return render_template("index.html")
    except Exception as e:
        error_message = str(e)
        return render_template("error.html", error_message=error_message)

@app.route('/log_in')
def log_in():
    return render_template('log_in.html')

@app.route('/users/<int:user_id>')
def user_movies(user_id):
    game.reset_game()
    user = data_manager.get_user(user_id)
    movies = data_manager.get_user_movies(user_id)
    for movie in movies:
        movie_id = movie['id']
        movie['countries_img'] = data_manager.movie_countries(movie_id)
    countries = data_manager.get_all_countries()
    if movies is None:
        return render_template('404.html'), 404
    return render_template('user_movies.html', movies=movies, user_id=user_id, user=user, countries=countries, data_manager=data_manager)

@app.route('/process_login', methods=['GET', 'POST'])
def process_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = data_manager.get_all_users()
        for user in users:
            if username == user['username'] and password == user['password']:
                user_id = user['id']
                return redirect(url_for('user_movies', user_id=user_id))
        error_message = "Incorrect username or password. Please try again."
        return render_template('log_in.html', error_message=error_message)
    return render_template('log_in.html')

@app.route('/users/<int:user_id>/add_movie', methods=['GET', 'POST'])
def add_movie(user_id):
    try:
        users = data_manager.get_all_users()
        if request.method == 'POST':
            user = next((user for user in users if user["id"] == user_id), None)
            if user:
                name_input = request.form.get('name')
                movie_json = api(name_input)
                if movie_json.get('Error'):
                    return render_template('error.html', error_message=movie_json.get('Error'))
                countries = movie_json['Country']
                countries_img = [country_flag(country) for country in countries.split(", ")]
                movies = data_manager.get_user_movies(user_id)
                new_id = 1 if not movies else max(movie['id'] for movie in movies) + 1
                movie_dict = {
                    'id': new_id,
                    'user_id': user_id,
                    'name': movie_json['Title'],
                    'director': movie_json['Director'],
                    'year': movie_json['Year'],
                    'rating': movie_json['imdbRating'],
                    'Poster': movie_json['Poster'],
                    'Countries': movie_json['Country'],
                    'countries_img': countries_img,
                    'genre': movie_json['Genre'],
                    'review': ""
                }
                data_manager.add_movie(movie_dict)
                return redirect(url_for('user_movies', user_id=user_id))
        return render_template('add_movie.html', user_id=user_id)
    except Exception as e:
        error_message = str(e)
        return render_template('error.html', error_message=error_message)

@app.route('/users/<int:user_id>/delete_movie/<int:movie_id>', methods=['POST'])
def delete_movie(user_id, movie_id):
    users = data_manager.get_all_users()
    for user in users:
        if user["id"] == user_id:
            movies = data_manager.get_user_movies(user_id)
            for movie in movies:
                if movie["id"] == movie_id:
                    data_manager.delete_movie(movie_id)
                    break
            break
    return redirect(url_for('user_movies', user_id=user_id))

@app.route('/users/<int:user_id>/update/<int:movie_id>', methods=['GET', 'POST'])
def update_movie(user_id, movie_id):
    if request.method == "POST":
        user = next((user for user in data_manager.get_all_users() if user["id"] == user_id), None)
        if user:
            movie = next((movie for movie in data_manager.get_user_movies(user_id) if movie["id"] == movie_id), None)
            if movie:
                movie_data = {
                    'id': movie_id,
                    'title': request.form.get("title"),
                    'director': movie["director"],
                    'year': request.form.get("year"),
                    'rating': request.form.get("rating"),
                    'poster': movie["poster"],
                    'review': movie["review"]
                }
                data_manager.update_movie(movie_id, movie_data)
                return redirect(url_for('user_movies', user_id=user_id))

    movies = data_manager.get_user_movies(user_id)
    if movies is None:
        return render_template('404.html'), 404

    movie = next((movie for movie in movies if movie["id"] == movie_id), None)
    if movie:
        return render_template('update_movie.html', user_id=user_id, movie=movie)
    return render_template('404.html'), 404

@app.route('/users/<int:user_id>/app_review_movie/<int:movie_id>', methods=['POST'])
def app_review_movie(user_id, movie_id):
    users = data_manager.get_all_users()
    for user in users:
        if user["id"] == user_id:
            movies = data_manager.get_user_movies(user_id)
            for movie in movies:
                if movie["id"] == movie_id:
                    title = movie["title"]
                    review = app_review(title)
                    movie_data = {"review": review}
                    data_manager.movie_app_review(movie_id, movie_data)
                    break
            break
    return redirect(url_for('user_movies', user_id=user_id))

@app.route('/users/<int:user_id>/delete_review_movie/<int:movie_id>', methods=['POST'])
def delete_review_movie(user_id, movie_id):
    users = data_manager.get_all_users()
    for user in users:
        if user["id"] == user_id:
            movies = data_manager.get_user_movies(user_id)
            for movie in movies:
                if movie["id"] == movie_id:
                    title = movie["title"]
                    review = ""
                    movie_data = {"review": review}
                    data_manager.movie_app_review(movie_id, movie_data)
                    break
            break
    return redirect(url_for('user_movies', user_id=user_id))

@app.route('/users/<int:user_id>/edit_profile', methods=['GET', 'POST'])
def edit_profile(user_id):
    try:
        if request.method == "POST":
            users = data_manager.get_all_users()
            for user in users:
                if user["id"] == user_id:
                    image = request.files.get('image')
                    image_filename = f'{user["username"]}.png'
                    if image:
                        image_filename = f'{user["username"]}.png'
                        image.save(f'static/{image_filename}')
                    user_data = {"username": request.form.get("username"), "password": request.form.get("password"),
                                 "image": image_filename}
                    data_manager.edit_profile(user_id, user_data)
                    break
            return redirect(url_for('user_movies', user_id=user_id))

        user = data_manager.get_user(user_id)
        return render_template('edit_profile.html', user=user)

    except Exception as e:
        error_message = str(e)
        return render_template('error.html', error_message=error_message), 500

@app.route('/users/<int:user_id>/movie_user_reviews/<string:movie_title>', methods=['GET', 'POST'])
def movie_user_reviews(user_id, movie_title):
    try:
        if request.method == 'POST':
            user = next((user for user in data_manager.get_all_users() if user["id"] == user_id), None)
            if user:
                movie_id = next((movie["id"] for movie in data_manager.get_user_movies(user_id) if movie["title"] == movie_title), None)
                if movie_id is not None:
                    rating = float(request.form.get('rating'))
                    comment = request.form.get('comment')
                    comment_data = {
                        'user_name': user['username'],
                        'rating': rating,
                        'comment': comment,
                        'img': user['image'],
                        'likes': 0,
                        'dislikes': 0,
                    }
                    data_manager.add_comment(comment_data, movie_title, user_id)
                    return redirect(url_for('movie_user_reviews', user_id=user_id, movie_title=movie_title))
            return render_template('404.html'), 404

        user = data_manager.get_user(user_id)
        movie_data = next((movie for movie in data_manager.get_user_movies(user_id) if movie["title"] == movie_title), None)
        if movie_data:
            movie_reviews = data_manager.get_comments(movie_data["title"])
            return render_template('movie_reviews.html', user_id=user_id, movie=movie_data, reviews=movie_reviews, user=user)
        else:
            return render_template('404.html'), 404

    except Exception as e:
        error_message = str(e)
        return render_template('error.html', error_message=error_message), 500

@app.route('/users/<int:user_id>/delete_review/<string:movie_title>/<int:review_id>', methods=['POST'])
def delete_review(user_id, movie_title, review_id):
    data_manager.delete_comment(movie_title, user_id, review_id)
    return redirect(url_for('movie_user_reviews', user_id=user_id, movie_title=movie_title))

@app.route('/users/<int:user_id>/movie_page/<int:movie_id>', methods=['GET', 'POST'])
def movie_page(user_id, movie_id):
    try:
        movies = data_manager.get_user_movies(user_id)
        if movies is None:
            return render_template('404.html'), 404
        selected_movie = None
        for movie in movies:
            if movie["id"] == movie_id:
                selected_movie = movie
                break
        if selected_movie is None:
            return render_template('404.html'), 404
        selected_movie['countries_img'] = data_manager.movie_countries(movie_id)
        countries = data_manager.get_all_countries()
        genres = data_manager.get_genre(movie_id)
        return render_template('movie_page.html', user_id=user_id, movie=selected_movie, genres=genres,
                               countries=countries, data_manager=data_manager)
    except Exception as e:
        error_message = str(e)
        return render_template('error.html', error_message=error_message), 500

@app.route('/trivia_game/<int:user_id>', methods=['GET', 'POST'])
def trivia_game(user_id):
    if game.game_q == 0:
        game.reset_game()
    return render_template('trivia_game.html', question=game.question, answers=game.answer_choices, user_id=user_id)

@app.route('/check_answer/<int:user_id>', methods=['POST'])
def check_answer(user_id):
    last_question = game.question
    user_answer = request.form.get('answer')
    is_correct = game.check(last_question, user_answer)
    result = "Correct!" if is_correct else "Incorrect. Try again!"
    if is_correct:
        game.score += 1
    game.game_q += 1
    if game.game_q == 5:
        return render_template('end_game.html', score=game.score, game_q=game.game_q, user_id=user_id)
    question_and_choices = game.trivia_game().split('?')
    game.question = question_and_choices[0].strip()
    game.answer_choices = question_and_choices[1].strip().split("\n")
    return render_template('trivia_game.html', question=game.question, answers=game.answer_choices, result=result, user_id=user_id)

@app.route('/users/<int:user_id>/like_review/<int:movie_id>/<int:review_id>', methods=['POST'])
def like_review(user_id, movie_id, review_id):
    users = data_manager.get_all_users()
    movie_title = ""
    for user in users:
        if user["id"] == user_id:
            movies = data_manager.get_user_movies(user_id)
            for movie in movies:
                if movie["id"] == movie_id:
                    movie_title = movie["title"]
                    data_manager.like_comment(movie["title"], review_id, user_id)
                    break
            break
    return redirect(url_for('movie_user_reviews', user_id=user_id, movie_title=movie_title))

@app.route('/users/<int:user_id>/dis_like_review/<int:movie_id>/<int:review_id>', methods=['POST'])
def dis_like_review(user_id, movie_id, review_id):
    users = data_manager.get_all_users()
    movie_title = ""
    for user in users:
        if user["id"] == user_id:
            movies = data_manager.get_user_movies(user_id)
            for movie in movies:
                if movie["id"] == movie_id:
                    movie_title = movie["title"]
                    data_manager.dislike_comment(movie["title"], review_id, user_id)
                    break
            break
    return redirect(url_for('movie_user_reviews', user_id=user_id, movie_title=movie_title))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
