from uuid import uuid4
from http import HTTPStatus
from flask import Flask, g, request
from backend.tool.logger import get_logger, init_logger_handler
from backend.tool.security import init_cors
from backend import config

logger = get_logger(__name__)

def create_app():
    app = Flask(__name__)
    app.config.from_object(config)

    init_logger_handler(app)
    init_controller(app)
    init_extensions(app)

    return app


def init_extensions(app):
    init_cors(app)


def init_controller(app):
    @app.errorhandler(400)
    def handle_400(e):
        import traceback
        traceback.print_exc()
        return {'message': 'Bad Request'}, HTTPStatus.BAD_REQUEST

    @app.errorhandler(404)
    def handle_404(e):
        return {'message': 'Not Found'}, HTTPStatus.NOT_FOUND

    @app.errorhandler(500)
    def handle_500(e):
        return {'message': 'Internal Server Error'}, HTTPStatus.INTERNAL_SERVER_ERROR

    from backend.controller import init_routes
    init_routes(app)
