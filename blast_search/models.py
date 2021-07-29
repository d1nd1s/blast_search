"Database models definitions"

import enum
import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Status(enum.Enum):
    "Task and request status values"
    CREATED = 1
    IN_PROGRESS = 2
    SUCCESS = 3
    ERROR = 4


class BlastType(enum.Enum):
    "Blast type values"
    BLASTN = 1
    BLASTP = 2


class Request(db.Model):
    "Model for Blast search requests"
    __tablename__ = 'request'
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column('status', db.Enum(Status))
    created_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    result = db.Column(db.Text())


class WorkerTask(db.Model):
    "Model for Blast search worker tasks"
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column('status', db.Enum(Status))
    query = db.Column(db.Text())
    database = db.Column(db.Text())
    result = db.Column(db.Text())
