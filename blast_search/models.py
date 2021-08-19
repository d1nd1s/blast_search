"Database models definitions"

import enum
import datetime
from dataclasses import dataclass

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Status(int, enum.Enum):
    "Task and request status values"
    CREATED: int = 1
    IN_PROGRESS: int = 2
    SUCCESS: int = 3
    ERROR: int = 4


class BlastType(str, enum.Enum):
    "Blast type values"
    BLASTN: str = 'blastn'
    BLASTP: str = 'blastp'


class WorkerStatus(int, enum.Enum):
    "Blast worker states"
    IDLE: int = 10
    BUSY: int = 20
    ERROR: int = 30


@dataclass
class BlastSearch(db.Model):
    "Model for Blast search requests"
    id: int
    status: Status
    created_date: datetime.datetime
    blast_type: BlastType
    db_name: str
    params: str
    result: str

    __tablename__ = 'search'
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column('status', db.Enum(Status))
    created_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    blast_type = db.Column('blast_type', db.Enum(BlastType))
    db_name = db.Column(db.String(100))
    blast_query = db.Column(db.Text())
    params = db.Column(db.Text())
    result = db.Column(db.Text())


@dataclass
class Worker(db.Model):
    "Model for Blast Workers"
    id: int
    url: str

    __tablename__ = 'workers'
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column('status', db.Enum(WorkerStatus))
    url = db.Column(db.String(50), nullable=False, unique=True)


@dataclass
class Task(db.Model):
    "Model for Blast search worker tasks"
    id: int
    status: Status
    created_date: datetime.datetime
    start_date: datetime.datetime
    blast_type: BlastType
    db_name: str
    db_part: int
    params: str
    result: str

    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column('status', db.Enum(Status))
    created_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    start_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    blast_type = db.Column('blast_type', db.Enum(BlastType))
    db_name = db.Column(db.String(100))
    db_part = db.Column(db.Integer, default=0)
    blast_query = db.Column(db.Text())
    params = db.Column(db.Text())
    result = db.Column(db.Text())
