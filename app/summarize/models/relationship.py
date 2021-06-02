from app.lib import BaseModel, db


class Relationship(BaseModel):
    type = db.Column(db.String(), nullable=False)
    field = db.Column(db.String(), nullable=False)
    related_field = db.Column(db.String(), nullable=False)
    description = db.Column(db.Text)

    resource_id = db.Column(
        db.Integer, db.ForeignKey("resource.id"), nullable=False
    )
    related_resource_id = db.Column(
        db.Integer, db.ForeignKey("resource.id"), nullable=False
    )

    def __repr__(self):
        return f"<Relationship type={self.type}>"
