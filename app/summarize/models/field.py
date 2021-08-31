from app.lib import NamedBaseModel, db


class Field(NamedBaseModel):
    __tablename__ = "field"

    # columns
    type = db.Column(db.String(), nullable=False)
    is_virtual = db.Column(db.Boolean(), default=False)
    is_primary_key = db.Column(db.Boolean(), default=False)
    is_archived = db.Column(db.Boolean, default=False, nullable=False)
    description = db.Column(db.Text)

    # references
    resource_name = db.Column(
        db.String(), db.ForeignKey("resource.name"), nullable=False
    )

    # relationships
    meta_data = db.relationship(
        "Metadata",
        foreign_keys="Metadata.field_name",
        backref="field",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f'<Field: name="{self.name}" type="{self.type}">'
