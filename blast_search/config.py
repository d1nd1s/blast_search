#!/usr/bin/env python

"""
Configuration module
Author: Sergey Bobkov
"""

import os
import json
from dataclasses import dataclass

class Config():
    "Flask configuration"
    DEBUG = True
    DEVELOPMENT = True
    SECRET_KEY = os.urandom(32)
    FLASK_SECRET = SECRET_KEY

    SQLALCHEMY_DATABASE_URI = 'sqlite:///requests.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    BLAST_DB_CONFIG = 'blast_search/data/blast_db.json'
    LOG_FILE = 'log.txt'


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
