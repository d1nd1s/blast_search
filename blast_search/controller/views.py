"Blast controller views"

from flask import jsonify, Blueprint

from blast_search.blast import blast


control_bp = Blueprint('control', __name__, url_prefix='/')


@control_bp.route('/')
def index():
    return jsonify({"message": "Hello, I'm a blast controller"})


@control_bp.route('/blast', methods=["POST"])
def blast():
    return jsonify({"status": "success",
                    "search_id": 10})


# @control_bp.route('/result/<int:req_id>')
# def result(req_id):

#     return jsonify({"status": "success",
#                     "result": blast.BlastResult.to_dict()})

@control_bp.route('/worker/new', methods=["POST"])
def new_worker():

    return jsonify({"status": "success"})


@control_bp.route('/worker/task/<int:task_id>', methods=["POST"])
def worker_report_task():

    return jsonify({"status": "success"})