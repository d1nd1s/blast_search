"Blast controller views"

import os
import requests
from tempfile import NamedTemporaryFile

from flask import current_app, jsonify, Blueprint, request

from blast_search.blast import blast
from blast_search.models import db, BlastSearch, Status, Worker, WorkerStatus, Task
from blast_search import request_data


control_bp = Blueprint('control', __name__, url_prefix='/')


@control_bp.before_app_first_request
def update_workers():
    for worker in db.session.query(Worker).all():
        try:
            requests.get(worker.url + '/ping')
        except requests.ConnectionError:
            db.session.delete(worker)
    db.session.commit()


@control_bp.route('/')
def index():
    return jsonify({"message": "Hello, I'm a blast controller"})


@control_bp.route(request_data.BLAST_DB_URL)
def db_list():
    "Get list of available databases"
    return jsonify(current_app.config['BLAST_DB'].to_dict())


def create_tasks():
    for search in BlastSearch.query.filter_by(status=Status.CREATED).all():
        task = Task(
            status = Status.CREATED,
            blast_type = search.blast_type,
            db_name = search.db_name,
            db_part = 0,
            blast_query = search.blast_query,
            params = search.params
        )
        db.session.add(task)

        search.status = Status.IN_PROGRESS
    
    db.session.commit()


@control_bp.route(request_data.BLAST_SEARCH_URL, methods=["POST"])
def new_search():
    req_data = request_data.BlastSearchRequest.from_json(request.json)

    search_req = BlastSearch(
        status = Status.CREATED,
        blast_query=req_data.blast_query,
        blast_type=req_data.blast_type,
        db_name=req_data.db_name,
        params=req_data.params.to_json()
    )

    db.session.add(search_req)
    db.session.commit()

    search_id = search_req.id

    create_tasks()

    return jsonify({"search_id": search_id})


    # with NamedTemporaryFile(mode="w+", delete=False) as query_file:
    #     query_file.write(search_req.query)

    # if search_req.program == BlastType.BLASTP:
    #     program = "blastp"
    #     db_path = current_app.config['BLAST_DB'].blastp[search_req.db_name]
    # else:
    #     program = "blastn"
    #     db_path = current_app.config['BLAST_DB'].blastn[search_req.db_name]

    # runner = blast.BlastRunner(program, db_path)
    # blast_result = runner.run(query_file, search_req.params)

    # search_req = Request(status=Status.SUCCESS, result=blast_result.to_json())
    # db.session.add(search_req)
    # db.session.commit()

    # os.remove(query_file.name)

    # search_id = search_req.id

    # return jsonify({"search_id": search_id})


@control_bp.route(request_data.BLAST_SEARCH_URL + '/<int:req_id>')
def search_result(req_id):
    search_req = BlastSearch.query.get(req_id)
    if search_req is None:
        return jsonify({"msg": "search id was not found"}), 404

    return jsonify(search_req)


@control_bp.route('/tasks')
def tasks():
    tasks = Task.query.all()
    return jsonify(
        {"status": "success",
         "tasks": tasks
    })


workers_bp = Blueprint('workers', __name__, url_prefix=request_data.BLAST_WORKERS_URL)

@workers_bp.route('', methods=["GET", "POST", "DELETE"])
def workers():
    if request.method == 'GET':
        wkrs = Worker.query.all()
        return jsonify(
            {"status": "success",
             "workers": wkrs
        })

    worker_ip = request.environ['REMOTE_ADDR']
    worker_port = request.json['port']
    worker_url = f"http://{worker_ip}:{worker_port}"

    if request.method == 'POST':
        if Worker.query.filter_by(url=worker_url).first() is not None:
            return jsonify({"status": "warning",
                            "msg": "worker is already in database"})

        worker = Worker(status=WorkerStatus.IDLE, url=worker_url)
        db.session.add(worker)
        db.session.commit()
        return jsonify({"status": "success"})

    if request.method == 'DELETE':
        #TODO: check for completed tasks
        worker = Worker.query.filter_by(url=worker_url).first()

        if worker is None:
            return jsonify({"status": "error", "msg": "worker is missing form database"}), 404

        db.session.delete(worker)
        db.session.commit()
        return jsonify({"status": "success"})
