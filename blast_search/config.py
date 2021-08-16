#!/usr/bin/env python

"""
Configuration module
Author: Sergey Bobkov
"""

import os
import json
from dataclasses import dataclass
from dataclasses_json.api import dataclass_json


class Config():
    "Flask configuration"
    DEBUG = True
    DEVELOPMENT = True
    SECRET_KEY = os.getenv('SECRET_KEY') or os.urandom(32)
    FLASK_SECRET = SECRET_KEY

    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI') or 'sqlite:///requests.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    BLAST_CONTROLLER_URL = os.getenv('BLAST_CONTROLLER_URL') or 'http://localhost:5010'
    BLAST_CONTROLLER_URL_BKP = os.getenv('BLAST_CONTROLLER_URL_BKP') or 'http://localhost:5011'
    BLAST_DB_CONFIG = os.getenv('BLAST_DB_CONFIG') or 'data/blast_db.json'
    BLAST_WORKER_PORT = os.getenv('BLAST_WORKER_PORT') or '5050'
    LOG_FILE = os.getenv('LOG_FILE') or 'log.txt'


@dataclass_json
@dataclass
class BlastDBConfig():
    "Blast data configuration"
    blastn: dict
    blastp: dict


def get_blast_db_config(config_file: str) -> BlastDBConfig:
    """ Parse config file into dataclass
    """

    with open(config_file) as json_file:
        data = json.load(json_file)

        blast_db_config = BlastDBConfig(
            blastn={e["name"]:e["path"] for e in data["blastn"]},
            blastp={e["name"]:e["path"] for e in data["blastp"]},
        )

    return blast_db_config
