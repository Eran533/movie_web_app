from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(50), unique=True)
    user_img = db.Column(db.String(50), unique=True)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.user_name,
            'email': self.email,
            'password': self.password,
            'image': self.user_img,
        }

class Movies(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(50))
    director = db.Column(db.String(50))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    poster = db.Column(db.String(255))
    review = db.Column(db.Text)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'director': self.director,
            'year': self.year,
            'rating': self.rating,
            'poster': self.poster,
            'review': self.review
        }

class Countries(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'), nullable=False)
    country_name = db.Column(db.String(50))
    country_img = db.Column(db.String(255))

    def to_dict(self):
        return {
            'id': self.id,
            'movie_id': self.movie_id,
            'country_name': self.country_name.split(',') if self.country_name else [],
            'country_img': self.country_img
        }

class Reviews(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    movie_title = db.Column(db.String(50))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user_name = db.Column(db.String(50))
    rating = db.Column(db.Float)
    comment = db.Column(db.String(255))
    img = db.Column(db.String(50))
    likes = db.Column(db.Integer)
    dislikes = db.Column(db.Integer)

    def to_dict(self):
        return {
            'id': self.id,
            'user_name': self.user_name,
            'rating': self.rating,
            'comment': self.comment,
            'img': self.img,
            'likes': self.likes,
            'dislikes': self.dislikes,
            'user_id': self.user_id
        }

class Genre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'), nullable=False)
    genre = db.Column(db.String(50))

    def to_dict(self):
        return {
            'genre': self.genre
        }

class UserReviewLikes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    review_id = db.Column(db.Integer, db.ForeignKey('reviews.id'), nullable=False)

class UserReviewDissLikes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    review_id = db.Column(db.Integer, db.ForeignKey('reviews.id'), nullable=False)
