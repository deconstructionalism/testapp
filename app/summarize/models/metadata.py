from app.lib import NamedBaseModel, db


class Metadata(NamedBaseModel):
    __tablename__ = "metadata"

    # columns
    value = db.Column(db.String(), nullable=False)
    description = db.Column(db.Text)

    # references
    field_name = db.Column(
        db.String(), db.ForeignKey("field.name"), nullable=False
    )

    def __repr__(self):
        return f'<Metadata: name="{self.name}">'
