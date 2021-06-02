from app.lib import BaseModel, db


class Field(BaseModel):
    name = db.Column(db.String(), nullable=False)
    type = db.Column(db.String(), nullable=False)
    is_virtual = db.Column(db.Boolean(), default=False)
    description = db.Column(db.Text)
    related_field_name = db.Column(db.String())

    resource_id = db.Column(
        db.Integer, db.ForeignKey("resource.id"), nullable=False
    )
    related_resource_id = db.Column(db.Integer, db.ForeignKey("resource.id"))
    meta = db.relationship("Metadata", backref="field", lazy=True)

    def __repr__(self):
        return f"<Field name={self.name}>"
