from app.lib import BaseModel, DatabaseTypesSQLAlchemy, db


class Resource(BaseModel):
    name = db.Column(db.String(), unique=True, nullable=False)
    type = db.Column(db.String(), nullable=False)
    database_type = db.Column(DatabaseTypesSQLAlchemy, nullable=False)
    source_link = db.Column(db.String())
    description = db.Column(db.Text)
    primary_key = db.Column(db.String())

    fields = db.relationship("Field", backref="resource", lazy=True)
    relationships = db.relationship(
        "Relationship", backref="resource", lazy=True
    )

    def __repr__(self):
        return f"<Resource name={self.name}>"
