"Init blast_search application"

import os
import logging
import requests

from flask import Flask
from flask_bootstrap import Bootstrap

from blast_search import config, request_data
from blast_search.models import db
from .views import search_bp


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        app.config.from_object(config.Config)
    else:
        app.config.from_mapping(test_config)

    os.makedirs(app.instance_path, exist_ok=True)

    Bootstrap(app)
    db.init_app(app)

    logging.basicConfig(level=logging.DEBUG,
                    handlers=[
                        logging.FileHandler(app.config['LOG_FILE']),
                        logging.StreamHandler()
                    ])

    app.register_blueprint(search_bp)

    db_url = app.config['BLAST_CONTROLLER_URL'] + request_data.BLAST_DB_URL
    db_resp = requests.get(db_url)
    app.config['BLAST_DB'] = config.BlastDBConfig.from_json(db_resp.text)

    return app
