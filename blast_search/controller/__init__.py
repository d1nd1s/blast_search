"Init blast_search application"

import os
import logging

from flask import Flask

from blast_search.config import Config
from blast_search.models import db
from .views import control_bp


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        app.config.from_object(Config)
    else:
        app.config.from_mapping(test_config)

    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)

    logging.basicConfig(level=logging.DEBUG,
                    handlers=[
                        logging.FileHandler(app.config['LOG_FILE']),
                        logging.StreamHandler()
                    ])

    app.register_blueprint(control_bp)

    return app
