from flask import Flask, redirect, jsonify
import os
from src.auth import auth
from src.bookmark import bookmarks
from src.database import db, Bookmark
from flask_jwt_extended import JWTManager
from src.constant.Http_status_codes import HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR
from flasgger import Swagger, swag_from
from src.config.swagger import template, swagger_config
from dotenv import load_dotenv


def create_app(test_config=None):
    load_dotenv()
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        app.config.from_mapping(SECRET_KEY=os.environ.get("SECRECT_KEY"),
                                SQLALCHEMY_DATABASE_URI=os.environ.get(
                                    "SQLALCHEMY_DB_URI"),
                                JWT_SECRECT_KEY=os.environ.get("SECRECT_KEY"),
                                JWT_COOKIE_SECURE=False,
                                JWT_TOKEN_LOCATION=['headers', 'cookies'],

                                SWAGGER={
                                    'title': "BookmarkS API",
                                    'uiversion': 3
        }

        )
    else:
        app.config.from_mapping(test_config)
    JWTManager(app)
    db.app = app
    db.init_app(app)
    app.register_blueprint(auth)
    app.register_blueprint(bookmarks)
    Swagger(app, config=swagger_config, template=template)

    @app.get('/<short_url>')
    @swag_from('./docs/bookmarks/short_url.yaml')
    def redirect_url(short_url):
        bookmark = Bookmark.query.filter_by(short_url=short_url).first_or_404()

        if bookmark:
            bookmark.visits = bookmark.visits + 1
            db.session.commit()

            return redirect(bookmark.url)

    @app.errorhandler(HTTP_404_NOT_FOUND)
    def handler_404(e):
        return jsonify({'error': 'not found'}), HTTP_404_NOT_FOUND

    @app.errorhandler(HTTP_500_INTERNAL_SERVER_ERROR)
    def handler_500(e):
        return jsonify({'error': 'Something went wrong, we are working on it!'}), HTTP_500_INTERNAL_SERVER_ERROR
    return app
