from sqlalchemy.exc import SQLAlchemyError
from data_models import USER, MOVIES, db, Countries, Reviews, Genre
from datamanager.dataManager_Interface import DataManagerInterface

class SQLiteDataManager(DataManagerInterface):
    def __init__(self, app):
        self.app = app
        with self.app.app_context():
            db.init_app(self.app)

    def get_all_users(self):
        all_users = USER.query.all()
        return [user.to_dict() for user in all_users]

    def get_all_countries(self):
        all_countries = Countries.query.all()
        return [country.to_dict() for country in all_countries]

    def movie_countries(self, movie_id):
        movie_countries = Countries.query.filter_by(movie_id=movie_id).all()
        return [country.to_dict() for country in movie_countries]

    def get_user_movies(self, user_id):
        user_movies = MOVIES.query.filter_by(user_id=user_id).all()
        movies_with_reviews = []
        for movie in user_movies:
            movie_data = movie.to_dict()
            movie_data["reviews"] = self.get_comments(movie.id)
            movies_with_reviews.append(movie_data)
        return movies_with_reviews

    def add_movie(self, movie):
        try:
            new_movie = MOVIES(
                user_id=movie["user_id"],
                title=movie['name'],
                director=movie['director'],
                year=movie['year'],
                rating=movie['rating'],
                poster=movie['Poster'],
                review=movie['review']
            )
            db.session.add(new_movie)
            db.session.commit()

            # Handling multiple countries
            if "Countries" in movie:
                countries_list = movie["Countries"].split(",")  # Split the string into a list of country names
                countries_img = movie.get("countries_img",
                                          [])  # Get the country image URLs list (or an empty list if not provided)

                for country_name, country_img in zip(countries_list, countries_img):
                    new_country = Countries(
                        movie_id=new_movie.id,
                        country_name=country_name.strip(),
                        country_img=country_img
                    )
                    db.session.add(new_country)

            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            raise e

    def update_movie(self, movie_id, movie_data):
        existing_movie = MOVIES.query.get(movie_id)
        if existing_movie:
            existing_movie.title = movie_data['title']
            existing_movie.director = movie_data['director']
            existing_movie.year = movie_data['year']
            existing_movie.rating = movie_data['rating']
            existing_movie.poster = movie_data['poster']
            existing_movie.review = movie_data['review']
            db.session.commit()
        else:
            raise ValueError("Movie with the given ID not found.")

    def delete_movie(self, movie_id):
        try:
            movie_to_delete = MOVIES.query.get(movie_id)
            db.session.delete(movie_to_delete)
            countries_to_delete = Countries.query.filter_by(movie_id=movie_id).all()
            for country in countries_to_delete:
                db.session.delete(country)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            raise e

    def get_user(self, user_id):
        user = USER.query.get(user_id)
        return user.to_dict() if user else None

    def add_user(self, user):
        new_user = USER(user_name = user["username"], password = user["password"], user_img = user["image"], email= user["email"])
        db.session.add(new_user)
        db.session.commit()

    def edit_profile(self, user_id, user_data):
        existing_user = USER.query.get(user_id)
        if existing_user:
            existing_user.user_name = user_data["username"]
            existing_user.password = user_data["password"]
            existing_user.user_img = user_data["image"]
            db.session.commit()
        else:
            raise ValueError("Movie with the given ID not found.")

    def movie_app_review(self, movie_id, movie_data):
        existing_movie = MOVIES.query.get(movie_id)
        existing_movie.review = movie_data['review']
        db.session.commit()

    def add_comment(self, comment_data, movie_title, user_id):
        new_comment = Reviews(
            user_id=user_id,
            movie_title=movie_title,
            user_name=comment_data['user_name'],
            rating=comment_data['rating'],
            comment=comment_data['comment'],
            img=comment_data['img']
        )
        db.session.add(new_comment)
        db.session.commit()

    def get_comments(self, movie_title):
        movie_reviews = Reviews.query.filter_by(movie_title=movie_title).all()
        return [review.to_dict() for review in movie_reviews]

    def add_genre(self, genre_data, movie_title):
        genre_list = genre_data['genre'].split(",")
        for genre in genre_list:
            new_comment = Genre(
                movie_title=movie_title,
                genre= genre
            )
            db.session.add(new_comment)
            db.session.commit()

    def get_genre(self, movie_title):
        genres = Genre.query.filter_by(movie_title=movie_title).all()
        return [genre.to_dict() for genre in genres]