from flask import Blueprint, jsonify, request
from movie_web_app.data_models import User, Movies, db

api = Blueprint('api', __name__)

@api.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    user_list = [user.to_dict() for user in users]
    return jsonify({'users': user_list})

@api.route('/users/<user_id>/movies', methods=['GET'])
def get_movies(user_id):
    movies = Movies.query.filter_by(user_id=user_id).all()
    movies_list = [movie.to_dict() for movie in movies]
    return jsonify({'movies': movies_list})

@api.route('/users/<user_id>/movies', methods=['POST'])
def add_movie(user_id):
    data = request.json
    if 'title' not in data:
        return jsonify({'error': 'Title is a required field'}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    new_movie = Movies(
        title=data['title'],
        director=data.get('director', None),
        year=data.get('year', None),
        rating=data.get('rating', None),
        poster=data.get('poster', None),
        review=data.get('review', None),
        user=user
    )

    db.session.add(new_movie)
    db.session.commit()

    return jsonify({'message': 'Movie added successfully'}), 201
