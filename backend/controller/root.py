import os
from http import HTTPStatus
from flask import Blueprint, send_file


bp = Blueprint("root", __name__)


@bp.route("", methods=["GET"])
def status():
    return {'status': 'ok'}, HTTPStatus.OK
