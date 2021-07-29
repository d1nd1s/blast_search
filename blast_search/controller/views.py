"Blast controller views"

from flask import jsonify, Blueprint


control_bp = Blueprint('control', __name__, url_prefix='/')


@control_bp.route('/')
def index():
    return jsonify({"message": "Hello, I'm a blast controller"})
