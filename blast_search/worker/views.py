"Blast worker views"

from flask import jsonify, Blueprint


worker_bp = Blueprint('worker', __name__, url_prefix='/')


@worker_bp.route('/submit', methods=["POST"])
def submit():
    return jsonify({"status": "success"})
