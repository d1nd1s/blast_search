"Blast worker views"

from flask import jsonify, Blueprint


worker_bp = Blueprint('control', __name__, url_prefix='/')


@worker_bp.route('/')
def index():
    return jsonify({"message": "Hello, I'm a blast worker"})
