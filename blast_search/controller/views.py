"Blast controller views"

import os
from tempfile import NamedTemporaryFile

from flask import current_app, jsonify, Blueprint, request

from blast_search.blast import blast
from blast_search.models import db, Request, BlastType, Status
from blast_search import request_data


control_bp = Blueprint('control', __name__, url_prefix='/')


@control_bp.route('/')
def index():
    return jsonify({"message": "Hello, I'm a blast controller"})


@control_bp.route(request_data.BLAST_DB_URL)
def db_list():
    "Get list of available databases"
    return jsonify(current_app.config['BLAST_DB'].to_dict())


@control_bp.route(request_data.BLAST_SEARCH_URL, methods=["POST"])
def new_search():
    search_req = request_data.BlastSearchRequest.from_json(request.json)

    with NamedTemporaryFile(mode="w+", delete=False) as query_file:
        query_file.write(search_req.query)

    if search_req.program == BlastType.BLASTP:
        program = "blastp"
        db_path = current_app.config['BLAST_DB'].blastp[search_req.db_name]
    else:
        program = "blastn"
        db_path = current_app.config['BLAST_DB'].blastn[search_req.db_name]

    runner = blast.BlastRunner(program, db_path)
    blast_result = runner.run(query_file, search_req.params)

    search_req = Request(status=Status.SUCCESS, result=blast_result.to_json())
    db.session.add(search_req)
    db.session.commit()

    os.remove(query_file.name)

    search_id = search_req.id

    return jsonify({"search_id": search_id})


@control_bp.route(request_data.BLAST_RESULT_URL + '/<int:req_id>')
def result(req_id):
    search_req = Request.query.get(req_id)
    if search_req is None:
        return jsonify({"msg": "search id did not found"}), 404

    blast_result = blast.BlastResult.from_json(search_req.result)

    return jsonify(blast_result.to_dict())

# @control_bp.route('/worker/new', methods=["POST"])
# def new_worker():

#     return jsonify({"status": "success"})


# @control_bp.route('/worker/task/<int:task_id>', methods=["POST"])
# def worker_report_task():

#     return jsonify({"status": "success"})