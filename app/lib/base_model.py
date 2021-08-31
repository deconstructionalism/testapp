from app.database import db
from sqlalchemy_serializer import SerializerMixin


class BaseModel(db.Model, SerializerMixin):
    """Abstract base model for all postgres sqlalchemy models."""

    __abstract__ = True

    # columns
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(
        db.DateTime,
        default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp(),
    )


class NamedBaseModel(db.Model, SerializerMixin):
    """Abstract base model for all postgres sqlalchemy models."""

    __abstract__ = True

    # columns
    name = db.Column(db.String(), primary_key=True)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(
        db.DateTime,
        default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp(),
    )
