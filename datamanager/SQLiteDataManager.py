from sqlalchemy.exc import SQLAlchemyError
from movie_web_app.data_models import User, Movies, db, Countries, Reviews, Genre, UserReviewLikes, UserReviewDissLikes
from movie_web_app.datamanager.dataManager_Interface import DataManagerInterface

class SQLiteDataManager(DataManagerInterface):
    def __init__(self, app):
        self.app = app
        with self.app.app_context():
            db.init_app(self.app)

    def get_all_users(self):
        all_users = User.query.all()
        return [user.to_dict() for user in all_users]

    def get_all_countries(self):
        all_countries = Countries.query.all()
        return [country.to_dict() for country in all_countries]

    def movie_countries(self, movie_id):
        movie_countries = Countries.query.filter_by(movie_id=movie_id).all()
        return [country.to_dict() for country in movie_countries]

    def get_user_movies(self, user_id):
        user_movies = Movies.query.filter_by(user_id=user_id).all()
        movies_with_reviews = []
        for movie in user_movies:
            movie_data = movie.to_dict()
            movie_data["reviews"] = self.get_comments(movie.id)
            movies_with_reviews.append(movie_data)
        return movies_with_reviews

    def add_movie(self, movie):
        try:
            new_movie = Movies(
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
            if "Countries" in movie:
                countries_list = movie["Countries"].split(",")
                countries_img = movie.get("countries_img", [])

                for country_name, country_img in zip(countries_list, countries_img):
                    new_country = Countries(
                        movie_id=new_movie.id,
                        country_name=country_name.strip(),
                        country_img=country_img
                    )
                    db.session.add(new_country)
                self.add_genre(new_movie.id, movie)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            raise e

    def update_movie(self, movie_id, movie_data):
        existing_movie = Movies.query.get(movie_id)
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

    def get_movie_title(self, movie_id):
        movie = Movies.query.get(movie_id)
        return movie.title if movie else None

    def delete_movie(self, movie_id):
        try:
            movie_to_delete = Movies.query.get(movie_id)
            if movie_to_delete:
                genres_to_delete = Genre.query.filter_by(movie_id=movie_to_delete.id).all()
                for genre in genres_to_delete:
                    db.session.delete(genre)
                db.session.delete(movie_to_delete)
                countries_to_delete = Countries.query.filter_by(movie_id=movie_id).all()
                for country in countries_to_delete:
                    db.session.delete(country)
                db.session.commit()
            else:
                raise ValueError("Movie with the given ID not found.")
        except SQLAlchemyError as e:
            db.session.rollback()
            raise e
    def get_user(self, user_id):
        user = User.query.get(user_id)
        return user.to_dict() if user else None

    def add_user(self, user):
        new_user = User(user_name = user["username"], password = user["password"], user_img = user["image"], email= user["email"])
        db.session.add(new_user)
        db.session.commit()

    def edit_profile(self, user_id, user_data):
        existing_user = User.query.get(user_id)
        if existing_user:
            existing_user.user_name = user_data["username"]
            existing_user.password = user_data["password"]
            existing_user.user_img = user_data["image"]
            db.session.commit()
        else:
            raise ValueError("Movie with the given ID not found.")

    def movie_app_review(self, movie_id, review_data):
        existing_movie = Movies.query.get(movie_id)
        existing_movie.review = review_data["review"]
        db.session.commit()

    def add_comment(self, comment_data, movie_title, user_id):
        new_comment = Reviews(
            user_id=user_id,
            movie_title=movie_title,
            user_name=comment_data['user_name'],
            rating=comment_data['rating'],
            comment=comment_data['comment'],
            img=comment_data['img'],
            likes=comment_data['likes'],
            dislikes = comment_data['dislikes']
        )
        db.session.add(new_comment)
        db.session.commit()

    def get_comments(self, movie_title):
        movie_reviews = Reviews.query.filter_by(movie_title=movie_title).all()
        return [review.to_dict() for review in movie_reviews]

    def delete_comment(self, movie_title, user_id, review_id):
        reviews_to_delete = Reviews.query.filter_by(movie_title=movie_title, user_id=user_id, id=review_id).all()
        for review in reviews_to_delete:
            db.session.delete(review)
        db.session.commit()

    def like_comment(self, movie_title, review_id, user_id):
        movie_reviews = Reviews.query.filter_by(movie_title=movie_title).all()
        for movie_review in movie_reviews:
            if movie_review.movie_title == movie_title and movie_review.id == review_id:
                if not self.has_user_liked_review(user_id, review_id):
                    movie_review.likes += 1
                    new_like = UserReviewLikes(user_id=user_id, review_id=review_id)
                    db.session.add(new_like)
                    db.session.commit()
                    return movie_review.to_dict()
                else:
                    movie_review.likes -= 1
                    existing_like = UserReviewLikes.query.filter_by(user_id=user_id, review_id=review_id).first()
                    if existing_like:
                        db.session.delete(existing_like)
                db.session.commit()
                return movie_review.to_dict()
        return None

    def has_user_liked_review(self, user_id, review_id):
        return UserReviewLikes.query.filter_by(user_id=user_id, review_id=review_id).first() is not None

    def has_user_disliked_review(self, user_id, review_id):
        return UserReviewDissLikes.query.filter_by(user_id=user_id, review_id=review_id).first() is not None

    def dislike_comment(self, movie_title, review_id, user_id):
        movie_reviews = Reviews.query.filter_by(movie_title=movie_title).all()
        for movie_review in movie_reviews:
            if movie_review.movie_title == movie_title and movie_review.id == review_id:
                if not self.has_user_disliked_review(user_id, review_id):  # Use the new function
                    movie_review.dislikes += 1
                    new_dislike = UserReviewDissLikes(user_id=user_id, review_id=review_id)
                    db.session.add(new_dislike)
                    db.session.commit()
                    return movie_review.to_dict()
                else:
                    movie_review.dislikes -= 1
                    existing_dislike = UserReviewDissLikes.query.filter_by(user_id=user_id, review_id=review_id).first()
                    if existing_dislike:
                        db.session.delete(existing_dislike)
                db.session.commit()
                return movie_review.to_dict()
        return None

    def add_genre(self, movie_id, genre_data):
        genre_list = genre_data['genre'].split(",")
        for genre in genre_list:
            new_genre = Genre(
                movie_id=movie_id,
                genre=genre
            )
            db.session.add(new_genre)
        db.session.commit()

    def get_genre(self, movie_id):
        genres = Genre.query.filter_by(movie_id=movie_id).all()
        return [genre.to_dict() for genre in genres]
