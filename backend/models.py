from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class UseCase(db.Model):
    __tablename__ = 'use_cases'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    requestor = db.Column(db.String, nullable=False)
    description = db.Column(db.Text, nullable=False)
    rationale = db.Column(db.Text, nullable=False)
    stage = db.Column(db.String, nullable=False)
    reviewed_by_ai_committee = db.Column(db.Boolean, default=False)
    date_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f"<UseCase {self.title}>"
