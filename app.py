import ssl
import requests
from flask import Flask, render_template, request, redirect, url_for
from data_models import db
from datamanager.SQLiteDataManager import SQLiteDataManager
import os
from email.message import EmailMessage
import smtplib
from api import api
import game

game_q = 0
score = 0
question = ""
answer_choices = []

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
        "X-RapidAPI-Key": "234f5498c9msh8226e93fd4984d6p11b844jsn286c0f051d2e",
        "X-RapidAPI-Host": "chatgpt-best-price.p.rapidapi.com"
    }

    response = requests.post(url, json=payload, headers=headers)
    review_text = response.json()['choices'][0]['message']['content']
    return review_text

app = Flask(__name__)
db_path = os.path.join(os.path.dirname(__file__), "datamanager", "moviwebapp.db")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
data_manager = SQLiteDataManager(app)
app.register_blueprint(api, url_prefix='/api')

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

@app.route('/', methods=['GET', 'POST'])
def home():
    users = data_manager.get_all_users()
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        image = request.files.get('image')
        confirm_password = request.form.get('confirm_password')
        if password != confirm_password:
            error_message = "Passwords do not match"
            return render_template("index.html", error_message=error_message)
        for account in users:
            if username.lower() == account["username"].lower() or email.lower() == account["email"].lower():
                error_message = "Username/Email already exists"
                return render_template("index.html", error_message=error_message)
        if not users:
            new_id = 1
        else:
            new_id = max(movie['id'] for movie in users) + 1

        image_filename = f'{username}.png'

        if image:
            try:
                image_filename = f'{username}.png'
                image.save(f'static/{image_filename}')
            except:
                error_message = "Failed to save the image file"
                return render_template("index.html", error_message=error_message)

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

@app.route('/log_in')
def log_in():
    return render_template('log_in.html')

@app.route('/users/<int:user_id>')
def user_movies(user_id):
    global game_q, score, question, answer_choices
    game_q = 0
    score = 0
    question = ""
    answer_choices = []
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
    return render_template('log_in.html')


@app.route('/users/<int:user_id>/add_movie', methods=['GET', 'POST'])
def add_movie(user_id):
    users = data_manager.get_all_users()
    if request.method == 'POST':
        for user in users:
            if user["id"] == user_id:
                name_input = request.form.get('name')
                movie_json = api(name_input)
                if movie_json.get('Error'):
                    error_message = movie_json.get('Error')
                    return render_template('error.html', error_message=error_message)

                countries = movie_json['Country']
                countries_img = []
                if "," in countries:
                    for country in countries.split(", "):
                        countries_img.append(country_flag(country))
                else:
                    countries_img.append(country_flag(countries))
                movies = data_manager.get_user_movies(user_id)
                if not movies:
                    new_id = 1
                else:
                    new_id = max(movie['id'] for movie in movies) + 1

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
                    'review': ""
                }

                data_manager.add_movie(movie_dict)
                genre_dict = {
                    'genre': movie_json['Genre']
                }
                data_manager.add_genre(genre_dict, movie_json['Title'])
                return redirect(url_for('user_movies', user_id=user_id))
    return render_template('add_movie.html', user_id=user_id)

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
        users = data_manager.get_all_users()
        for user in users:
            if user["id"] == user_id:
                movies = data_manager.get_user_movies(user_id)
                for movie in movies:
                    if movie["id"] == movie_id:
                        title = request.form.get("title")
                        year = request.form.get("year")
                        rating = request.form.get("rating")
                        movie_data = {
                            'id': movie_id,
                            'title': title,
                            'director': movie["director"],
                            'year': year,
                            'rating': rating,
                            'poster': movie["poster"],
                            'review': movie["review"]
                        }
                        data_manager.update_movie(movie_id, movie_data)
                        break
                break
        return redirect(url_for('user_movies', user_id=user_id))
    else:
        movies = data_manager.get_user_movies(user_id)
        if movies is None:
            return render_template('404.html'), 404

        for movie in movies:
            if movie["id"] == movie_id:
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

@app.route('/users/<int:user_id>/edit_profile', methods=['GET', 'POST'])
def edit_profile(user_id):
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

@app.route('/users/<int:user_id>/movie_user_reviews/<string:movie_title>', methods=['GET', 'POST'])
def movie_user_reviews(user_id, movie_title):
    if request.method == 'POST':
        users = data_manager.get_all_users()
        for user in users:
            if user["id"] == user_id:
                movie_id = None
                user_movies = data_manager.get_user_movies(user_id)
                for movie in user_movies:
                    if movie["title"] == movie_title:
                        movie_id = movie["id"]
                        break
                if movie_id is not None:
                    rating = float(request.form.get('rating'))
                    comment = request.form.get('comment')
                    comment_data = {
                        'user_name': user['username'],
                        'rating': rating,
                        'comment': comment,
                        'img': user['image']
                    }
                    data_manager.add_comment(comment_data, movie_title, user_id)
                    return redirect(url_for('movie_user_reviews', user_id=user_id, movie_title=movie_title))
        return render_template('404.html'), 404

    user = data_manager.get_user(user_id)
    user_movies = data_manager.get_user_movies(user_id)
    movie_data = None
    for movie in user_movies:
        if movie["title"] == movie_title:
            movie_data = movie
            break
    if movie_data is not None:
        movie_reviews = data_manager.get_comments(movie_data["title"])
        return render_template('movie_reviews.html', user=user, movie=movie_data, reviews=movie_reviews)
    else:
        return render_template('404.html'), 404

@app.route('/users/<int:user_id>/movie_page/<int:movie_id>', methods=['GET', 'POST'])
def movie_page(user_id, movie_id):
    movies = data_manager.get_user_movies(user_id)
    if movies is None:
        return render_template('404.html'), 404
    for movie in movies:
        if movie["id"] == movie_id:
            movie_title = movie['title']
            movie['countries_img'] = data_manager.movie_countries(movie_id)
            countries = data_manager.get_all_countries()
            genres = data_manager.get_genre(movie_title)
            return render_template('movie_page.html', user_id=user_id, movie=movie, genres=genres, countries=countries, data_manager=data_manager)
    return render_template('404.html'), 404

def reset_game():
    global game_q, score, question, answer_choices
    score = 0
    game_q = 0
    question, answer_choices = game.trivia_game().split('?')
    question = question.strip()
    answer_choices = answer_choices.strip().split("\n")

@app.route('/trivia_game/<int:user_id>', methods=['GET', 'POST'])
def trivia_game(user_id):
    global game_q, score, question, answer_choices
    if game_q == 0:
        reset_game()
    return render_template('trivia_game.html', question=question, answers=answer_choices, user_id=user_id)

@app.route('/check_answer/<int:user_id>', methods=['POST'])
def check_answer(user_id):
    global game_q, score, question, answer_choices
    last_question = question
    user_answer = request.form.get('answer')
    correct_answer = game.correct_answer(last_question)
    is_correct = game.check(user_answer, correct_answer)
    result = "Correct!" if is_correct else "Incorrect. Try again!"
    if is_correct:
        score += 1
    game_q += 1
    if game_q == 5:
        return render_template('end_game.html', score=score, game_q=game_q, user_id=user_id)
    question, answer_choices = game.trivia_game().split('?')
    question = question.strip()
    answer_choices = answer_choices.strip().split("\n")
    return render_template('trivia_game.html', question=question, answers=answer_choices, result=result, user_id=user_id)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
