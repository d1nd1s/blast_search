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

    DATA_CONFIG = 'data.json'
    LOG_FILE = 'log.txt'


@dataclass
class DataConfig():
    "Blast data configuration"
    db_blast_n: dict
    db_blast_p: dict


def get_data_config(config_file: str) -> DataConfig:
    """ Parse config file into dataclass
    """

    with open(config_file) as json_file:
        data = json.load(json_file)

        data_config = DataConfig(
            db_blast_n={e["name"]:e["path"] for e in data["blastn"]},
            db_blast_p={e["name"]:e["path"] for e in data["blastp"]},
        )

    return data_config
