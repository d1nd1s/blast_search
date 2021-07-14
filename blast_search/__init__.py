"Init blast_search application"

import os
import logging

import click
from flask import Flask, g
from flask.cli import with_appcontext
from flask_bootstrap import Bootstrap

from .config import Config, get_blast_db_config
from .models import db
from .views import search_bp


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        app.config.from_object(Config)
    else:
        app.config.from_mapping(test_config)

    os.makedirs(app.instance_path, exist_ok=True)

    Bootstrap(app)
    db.init_app(app)
    app.cli.add_command(init_db_command)

    logging.basicConfig(level=logging.DEBUG,
                    handlers=[
                        logging.FileHandler(app.config['LOG_FILE']),
                        logging.StreamHandler()
                    ])

    app.config['BLAST_DB'] = get_blast_db_config(app.config['BLAST_DB_CONFIG'])

    app.register_blueprint(search_bp)

    return app


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    db.create_all()
    click.echo('Initialized the database.')
