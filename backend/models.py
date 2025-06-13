from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# In a larger application, the db instance would typically be managed
# centrally and imported here. For this example, if models.py were to be
# used independently for schema management (e.g. with Alembic),
# it might initialize its own db instance. However, to keep it strictly
# aligned with app.py's definition for now, we'll define the model structure.
# The actual db instance used by the Flask app is the one in app.py.
db = SQLAlchemy()

class UseCase(db.Model):
    """
    Represents an AI use case tracked by the system.

    Attributes:
        id (int): Primary key, unique identifier for the use case.
        title (str): The title of the use case (max 100 chars).
        requestor (str): The person or entity requesting the use case (max 100 chars).
        description (str): A detailed description of the use case.
        rationale (str): The justification or reasons for implementing the use case.
        stage (str): The current stage of development or review for the use case (max 50 chars)
                     (e.g., 'Initial Idea', 'Development', 'Review', 'Approved').
        reviewed_by_ai_committee (bool): Flag indicating if the AI committee has reviewed this use case.
                                         Defaults to False.
        date_updated (datetime): Timestamp of the last update. Automatically set on update.
        updated_by (str): Identifier of the user who last updated the use case (max 100 chars).
    """
    __tablename__ = 'use_cases'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    requestor = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    rationale = db.Column(db.Text, nullable=False)
    stage = db.Column(db.String(50), nullable=False)
    reviewed_by_ai_committee = db.Column(db.Boolean, default=False)
    date_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = db.Column(db.String(100), nullable=False)

    def to_dict(self):
        """Serializes the UseCase SQLAlchemy model object to a Python dictionary."""
        return {
            'id': self.id,
            'title': self.title,
            'requestor': self.requestor,
            'description': self.description,
            'rationale': self.rationale,
            'stage': self.stage,
            'reviewed_by_ai_committee': self.reviewed_by_ai_committee,
            'date_updated': self.date_updated.isoformat() if self.date_updated else None,
            'updated_by': self.updated_by
        }

    def __repr__(self):
        """Returns a string representation of the UseCase object, primarily for debugging."""
        return f"<UseCase {self.title}>"
