"Database models definitions"

import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Request(db.Model):
    "Model for Blast search requests"
    __tablename__ = 'request'
    id = db.Column(db.Integer, primary_key=True)
    created_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    data = db.Column(db.Text())
