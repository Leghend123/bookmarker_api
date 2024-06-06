from flasgger import swag_from
from flask import Blueprint, request, jsonify
from src.constant.Http_status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_401_UNAUTHORIZED, HTTP_204_NO_CONTENT, HTTP_202_ACCEPTED, HTTP_400_BAD_REQUEST, HTTP_409_CONFLICT
from werkzeug.security import check_password_hash, generate_password_hash
import validators
from src.database import User, db
from flask_jwt_extended import create_refresh_token, create_access_token, jwt_required, get_jwt_identity, unset_jwt_cookies, set_access_cookies
auth = Blueprint("auth", __name__, url_prefix="/api/v1/auth")


@auth.post('/register')
@swag_from('./docs/auth/register.yaml')
def register():
    username = request.json.get("username")
    email = request.json.get("email")
    password = request.json.get("password")

    if len(password) < 6:
        return jsonify({
            "Error": "Password too short"
        }), HTTP_400_BAD_REQUEST

    if len(username) < 3:
        return jsonify({
            "Error": "Username is too short"
        }), HTTP_400_BAD_REQUEST

    if not username.isalnum() or " " in username:
        return jsonify({
            "Error": "Username is not alphanumeric and no space"
        }), HTTP_400_BAD_REQUEST

    if not validators.email(email):
        return jsonify({
            "Error": "Email is not valid"
        }), HTTP_400_BAD_REQUEST

    if User.query.filter_by(email=email).first() is not None:
        return jsonify({
            "Error": "Email is taken"
        }), HTTP_409_CONFLICT

    if User.query.filter_by(username=username).first() is not None:
        return jsonify({
            "Error": "Username is taken"
        }), HTTP_409_CONFLICT

    password_hash = generate_password_hash(password)

    user = User(username=username, email=email, password=password_hash)
    db.session.add(user)
    db.session.commit()
    return jsonify({
        'message': "user created",
        'user': {
            'username': username,
            'email': email
        }
    }), HTTP_201_CREATED


@auth.post('/login')
@swag_from('./docs/auth/login.yaml')
def login():
    email = request.json.get("email", None)
    password = request.json.get("password", None)

    user = User.query.filter_by(email=email).first()
    if user:
        _is_correct_pass = check_password_hash(user.password, password)

        if _is_correct_pass:
            access_token = create_access_token(identity=user.id)
            refresh_token = create_refresh_token(identity=user.id)
            response = jsonify({"msg": "login success"})
            set_access_cookies(response, access_token)

            return jsonify({
                'user': {
                    'Refresh': refresh_token,
                    'Access': access_token,
                    'Username': user.username,
                    'email': user.email,

                }

            }), HTTP_200_OK

    return jsonify({'Error': "wrong credentails"}), HTTP_401_UNAUTHORIZED


@auth.get('/me')
@jwt_required()
@swag_from('./docs/auth/home.yaml')
def me():
    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()

    return jsonify({
        "username": user.username,
        "emal": user.email
    }), HTTP_200_OK


@auth.post('/refresh')
@jwt_required(refresh=True)
@swag_from('./docs/auth/refresh.yaml')
def refresh_user_token():
    identity = get_jwt_identity()
    access = create_access_token(identity=identity)
    response = jsonify({"msg": "refreshed"})
    set_access_cookies(response, access)

    return jsonify({
        "Access": access
    }), HTTP_200_OK


@auth.post('/logout')
@swag_from('./docs/auth/logout.yaml')
def logout():
    response = jsonify({"msg": "logout successful"})
    unset_jwt_cookies(response)
    return response
