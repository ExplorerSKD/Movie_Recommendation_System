from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# TMDB API configuration
TMDB_API_KEY = os.getenv('TMDB_API_KEY')
TMDB_ACCESS_TOKEN = os.getenv('TMDB_ACCESS_TOKEN')
TMDB_BASE_URL = 'https://api.themoviedb.org/3'
TMDB_IMAGE_BASE_URL = 'https://image.tmdb.org/t/p/w500'

# Mock user data (in a real app, this would be in a database)
USERS = {
    1: {'name': 'Alice', 'ratings': {1: 5, 2: 4, 8: 5, 13: 4}},
    2: {'name': 'Bob', 'ratings': {3: 5, 7: 4, 14: 5, 15: 3}},
    3: {'name': 'Charlie', 'ratings': {1: 5, 3: 4, 8: 4, 14: 4}},
    4: {'name': 'Diana', 'ratings': {4: 5, 9: 5, 16: 5, 6: 3}},
    5: {'name': 'Eve', 'ratings': {10: 5, 12: 4, 18: 5}},
    6: {'name': 'Frank', 'ratings': {6: 5, 5: 4, 17: 5}},
    7: {'name': 'Grace', 'ratings': {11: 5, 19: 5, 4: 4}},
}

# Mood mapping for genres
GENRE_MOODS = {
    'Action': ['Exciting', 'Intense', 'Epic'],
    'Adventure': ['Exciting', 'Epic', 'Funny'],
    'Animation': ['Whimsical', 'Heartwarming', 'Funny'],
    'Comedy': ['Funny', 'Lighthearted', 'Quirky'],
    'Crime': ['Dark', 'Intense', 'Mysterious'],
    'Documentary': ['Thought-provoking', 'Informative'],
    'Drama': ['Emotional', 'Heartwarming', 'Thought-provoking'],
    'Family': ['Heartwarming', 'Funny', 'Whimsical'],
    'Fantasy': ['Whimsical', 'Epic', 'Exciting'],
    'History': ['Epic', 'Thought-provoking', 'Emotional'],
    'Horror': ['Dark', 'Intense', 'Scary'],
    'Music': ['Emotional', 'Funny', 'Heartwarming'],
    'Mystery': ['Mysterious', 'Thought-provoking', 'Intense'],
    'Romance': ['Emotional', 'Heartwarming', 'Funny'],
    'Science Fiction': ['Thought-provoking', 'Exciting', 'Dark'],
    'TV Movie': ['Lighthearted', 'Emotional'],
    'Thriller': ['Intense', 'Mysterious', 'Dark'],
    'War': ['Epic', 'Intense', 'Emotional'],
    'Western': ['Epic', 'Exciting', 'Intense']
}

def get_tmdb_headers():
    return {
        'Authorization': f'Bearer {TMDB_ACCESS_TOKEN}',
        'Content-Type': 'application/json;charset=utf-8'
    }

@app.route('/api/users', methods=['GET'])
def get_users():
    return jsonify(USERS)

@app.route('/api/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = USERS.get(user_id)
    if user:
        return jsonify(user)
    return jsonify({'error': 'User not found'}), 404

@app.route('/api/movies/discover', methods=['GET'])
def discover_movies():
    genre = request.args.get('genre', '')
    page = request.args.get('page', 1)
    
    url = f'{TMDB_BASE_URL}/discover/movie'
    params = {
        'api_key': TMDB_API_KEY,
        'language': 'en-US',
        'sort_by': 'popularity.desc',
        'page': page,
        'with_genres': genre
    }
    
    response = requests.get(url, params=params, headers=get_tmdb_headers())
    data = response.json()
    
    movies = []
    for movie in data.get('results', []):
        # Get the primary genre name
        genre_name = 'Unknown'
        if movie.get('genre_ids'):
            # Get genre details
            genre_url = f'{TMDB_BASE_URL}/genre/movie/list'
            genre_params = {'api_key': TMDB_API_KEY, 'language': 'en-US'}
            genre_response = requests.get(genre_url, params=genre_params, headers=get_tmdb_headers())
            genre_data = genre_response.json()
            
            for genre in genre_data.get('genres', []):
                if genre['id'] == movie['genre_ids'][0]:
                    genre_name = genre['name']
                    break
        
        # Map moods based on genre
        moods = GENRE_MOODS.get(genre_name, ['Entertaining'])
        
        movies.append({
            'id': movie['id'],
            'title': movie['title'],
            'genre': genre_name,
            'avgRating': movie['vote_average'],
            'imageUrl': f"{TMDB_IMAGE_BASE_URL}{movie['poster_path']}" if movie['poster_path'] else 'https://placehold.co/500x750/1a1a1a/ffffff?text=No+Image',
            'type': 'Movie',
            'moods': moods,
            'overview': movie['overview'],
            'releaseDate': movie['release_date']
        })
    
    return jsonify({
        'movies': movies,
        'totalPages': data.get('total_pages', 1),
        'currentPage': data.get('page', 1)
    })

@app.route('/api/movies/search', methods=['GET'])
def search_movies():
    query = request.args.get('query', '')
    page = request.args.get('page', 1)
    
    if not query:
        return jsonify({'error': 'Query parameter is required'}), 400
    
    url = f'{TMDB_BASE_URL}/search/movie'
    params = {
        'api_key': TMDB_API_KEY,
        'language': 'en-US',
        'query': query,
        'page': page
    }
    
    response = requests.get(url, params=params, headers=get_tmdb_headers())
    data = response.json()
    
    movies = []
    for movie in data.get('results', []):
        # Get the primary genre name
        genre_name = 'Unknown'
        if movie.get('genre_ids'):
            # Get genre details
            genre_url = f'{TMDB_BASE_URL}/genre/movie/list'
            genre_params = {'api_key': TMDB_API_KEY, 'language': 'en-US'}
            genre_response = requests.get(genre_url, params=genre_params, headers=get_tmdb_headers())
            genre_data = genre_response.json()
            
            for genre in genre_data.get('genres', []):
                if genre['id'] == movie['genre_ids'][0]:
                    genre_name = genre['name']
                    break
        
        # Map moods based on genre
        moods = GENRE_MOODS.get(genre_name, ['Entertaining'])
        
        movies.append({
            'id': movie['id'],
            'title': movie['title'],
            'genre': genre_name,
            'avgRating': movie['vote_average'],
            'imageUrl': f"{TMDB_IMAGE_BASE_URL}{movie['poster_path']}" if movie['poster_path'] else 'https://placehold.co/500x750/1a1a1a/ffffff?text=No+Image',
            'type': 'Movie',
            'moods': moods,
            'overview': movie['overview'],
            'releaseDate': movie['release_date']
        })
    
    return jsonify({
        'movies': movies,
        'totalPages': data.get('total_pages', 1),
        'currentPage': data.get('page', 1)
    })

@app.route('/api/movies/recommendations', methods=['GET'])
def get_recommendations():
    user_id = request.args.get('user_id', 1)
    user = USERS.get(int(user_id))
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Get user's rated movies
    user_ratings = user['ratings']
    
    # Content-based recommendations
    content_recs = get_content_based_recommendations(user_ratings)
    
    # Collaborative filtering recommendations
    collab_recs = get_collaborative_recommendations(int(user_id), user_ratings)
    
    # Hybrid recommendations (combine both approaches)
    hybrid_recs = get_hybrid_recommendations(content_recs, collab_recs)
    
    return jsonify({
        'contentBased': content_recs[:5],
        'collaborative': collab_recs[:5],
        'hybrid': hybrid_recs[:5]
    })

def get_content_based_recommendations(user_ratings):
    # Get user's favorite genres based on ratings
    genre_scores = {}
    for movie_id, rating in user_ratings.items():
        # In a real app, we'd fetch movie details from TMDB
        # For demo purposes, we'll use a simplified approach
        pass
    
    # For demo, return popular movies
    url = f'{TMDB_BASE_URL}/movie/popular'
    params = {
        'api_key': TMDB_API_KEY,
        'language': 'en-US',
        'page': 1
    }
    
    response = requests.get(url, params=params, headers=get_tmdb_headers())
    data = response.json()
    
    recommendations = []
    for movie in data.get('results', [])[:10]:
        # Get the primary genre name
        genre_name = 'Unknown'
        if movie.get('genre_ids'):
            # Get genre details
            genre_url = f'{TMDB_BASE_URL}/genre/movie/list'
            genre_params = {'api_key': TMDB_API_KEY, 'language': 'en-US'}
            genre_response = requests.get(genre_url, params=genre_params, headers=get_tmdb_headers())
            genre_data = genre_response.json()
            
            for genre in genre_data.get('genres', []):
                if genre['id'] == movie['genre_ids'][0]:
                    genre_name = genre['name']
                    break
        
        # Map moods based on genre
        moods = GENRE_MOODS.get(genre_name, ['Entertaining'])
        
        recommendations.append({
            'id': movie['id'],
            'title': movie['title'],
            'genre': genre_name,
            'avgRating': movie['vote_average'],
            'imageUrl': f"{TMDB_IMAGE_BASE_URL}{movie['poster_path']}" if movie['poster_path'] else 'https://placehold.co/500x750/1a1a1a/ffffff?text=No+Image',
            'type': 'Movie',
            'moods': moods,
            'overview': movie['overview'],
            'releaseDate': movie['release_date']
        })
    
    return recommendations

def get_collaborative_recommendations(user_id, user_ratings):
    # Find similar users
    similar_users = []
    for uid, user_data in USERS.items():
        if uid == user_id:
            continue
        
        similarity = 0
        for movie_id, rating in user_ratings.items():
            if movie_id in user_data['ratings']:
                # Simple similarity calculation
                similarity += 1
        
        similar_users.append({'id': uid, 'similarity': similarity, 'ratings': user_data['ratings']})
    
    # Sort by similarity
    similar_users.sort(key=lambda x: x['similarity'], reverse=True)
    
    # Get recommendations from similar users
    recommendations = []
    for user in similar_users[:3]:  # Top 3 similar users
        for movie_id, rating in user['ratings'].items():
            if rating >= 4 and movie_id not in user_ratings:
                # In a real app, we'd fetch movie details from TMDB
                # For demo, we'll just add the movie ID
                recommendations.append(int(movie_id))
    
    # Fetch movie details for recommended IDs
    movie_details = []
    for movie_id in set(recommendations)[:10]:  # Get unique IDs, limit to 10
        url = f'{TMDB_BASE_URL}/movie/{movie_id}'
        params = {
            'api_key': TMDB_API_KEY,
            'language': 'en-US'
        }
        
        response = requests.get(url, params=params, headers=get_tmdb_headers())
        movie = response.json()
        
        # Get the primary genre name
        genre_name = 'Unknown'
        if movie.get('genres'):
            genre_name = movie['genres'][0]['name'] if movie['genres'] else 'Unknown'
        
        # Map moods based on genre
        moods = GENRE_MOODS.get(genre_name, ['Entertaining'])
        
        movie_details.append({
            'id': movie['id'],
            'title': movie['title'],
            'genre': genre_name,
            'avgRating': movie['vote_average'],
            'imageUrl': f"{TMDB_IMAGE_BASE_URL}{movie['poster_path']}" if movie.get('poster_path') else 'https://placehold.co/500x750/1a1a1a/ffffff?text=No+Image',
            'type': 'Movie',
            'moods': moods,
            'overview': movie['overview'],
            'releaseDate': movie['release_date']
        })
    
    return movie_details

def get_hybrid_recommendations(content_recs, collab_recs):
    # Combine and deduplicate recommendations
    all_recs = content_recs + collab_recs
    unique_recs = []
    seen_ids = set()
    
    for movie in all_recs:
        if movie['id'] not in seen_ids:
            unique_recs.append(movie)
            seen_ids.add(movie['id'])
    
    return unique_recs[:10]  # Return top 10 unique recommendations

if __name__ == '__main__':
    app.run(debug=True, port=5000)