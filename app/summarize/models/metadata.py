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

    # relationships
    metadata_filters = db.relationship(
        "MetadataFilter",
        foreign_keys="MetadataFilter.metadata_name",
        backref="metadata",
        cascade="all, delete-orphan",
        uselist=False,
    )

    def __repr__(self):
        return f'<Metadata: name="{self.name}">'
