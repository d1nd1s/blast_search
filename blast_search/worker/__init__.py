"Init blast_search application"

import os
import logging
import atexit
import requests

from flask import Flask

from blast_search import request_data
from blast_search.config import Config
from .views import worker_bp


def on_exit(work_url, work_json):
    requests.delete(work_url, json=work_json)


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        app.config.from_object(Config)
    else:
        app.config.from_mapping(test_config)

    os.makedirs(app.instance_path, exist_ok=True)

    logging.basicConfig(level=logging.DEBUG,
                    handlers=[
                        logging.FileHandler(app.config['LOG_FILE']),
                        logging.StreamHandler()
                    ])

    app.register_blueprint(worker_bp)

    work_url = app.config['BLAST_CONTROLLER_URL'] + request_data.BLAST_WORKERS_URL
    work_json = {'port': app.config['BLAST_WORKER_PORT']}

    try:
        work_resp = requests.post(work_url, json=work_json)
        if not work_resp.ok:
            raise ValueError('Error connecting to controller')

        atexit.register(on_exit, work_url=work_url, work_json=work_json)
    except requests.ConnectionError as exc:
        raise ValueError('Cannot connect to controller') from exc


    return app
