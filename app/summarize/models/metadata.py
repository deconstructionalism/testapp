from app.lib import BaseModel, db


class MetaData(BaseModel):
    name = db.Column(db.String(), nullable=False)
    value = db.Column(db.String(), nullable=False)
    description = db.Column(db.Text)

    field_id = db.Column(
        db.Integer, db.ForeignKey("field.id"), nullable=False
    )

    def __repr__(self):
        return f"<Metadata name={self.name}>"
