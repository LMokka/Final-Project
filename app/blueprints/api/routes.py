from . import api
from .auth import basic_auth, token_auth
from flask import jsonify, request
from app.models import Post, User


@api.route('/token')
@basic_auth.login_required
def get_token():
    user = basic_auth.current_user()
    token = user.get_token()
    return jsonify({'token': token, 'token_expiration': user.token_expiration})


@api.route('/posts', methods=["GET"])
def get_posts():
    posts = Post.query.all()
    return jsonify([p.to_dict() for p in posts])


@api.route('/posts/<post_id>')
def get_post(post_id):
    post = Post.query.get_or_404(post_id)
    return jsonify(post.to_dict())


@api.route('/posts', methods=["POST"])
@token_auth.login_required
def create_post():
    if not request.is_json:
        return jsonify({'error': 'Your request content-type must be application/json'}), 400
    # Get the data from the request body
    data = request.json
    print(data, type(data))
    # Validate the data
    for field in ['title', 'body']:
        if field not in data:
            # if field not in request body, respond with a 400 error
            return jsonify({'error': f"'{field}' must be in request body"}), 400
    
    # Get fields from data dict
    title = data.get('title')
    body = data.get('body')
    user = token_auth.current_user()
    user_id = user.id
    # Create new instance of post with data
    new_post = Post(title=title, body=body, user_id=user_id)
    return jsonify(new_post.to_dict()), 201


# Get a user by user_id
@api.route('/users/<user_id>')
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())


# Create a new user
@api.route('/users', methods=["POST"])
def create_user():
    # Check to make sure there is a JSON body on the request
    if not request.is_json:
        return jsonify({"error": "Your request content-type must be application/json"}), 400
    # Get data from request
    data = request.json
    # Make sure data has all of the required fields
    for field in ['email', 'username', 'password']:
        if field not in data:
            return jsonify({"error": f"'{field}' must be in request body"}), 400
    # Getting the data from the dictionary
    email = data.get('email')
    username = data.get('username')
    password = data.get('password')
    # Before we add the user to the database, check to see if there is already a user with username or email
    existing_user = User.query.filter((User.email == email) | (User.username == username)).first()
    if existing_user:
        return jsonify({"error": "User with username and/or email already exists"}), 400
    # Create new user with request data
    new_user = User(email=email, username=username, password=password)
    return jsonify(new_user.to_dict()), 201