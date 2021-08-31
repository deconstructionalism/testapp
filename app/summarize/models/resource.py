from app.lib import NamedBaseModel, DatabaseTypesSQLAlchemy, db


class Resource(NamedBaseModel):
    __tablename__ = "resource"

    # columns
    type = db.Column(db.String(), nullable=False)
    app = db.Column(db.String(), nullable=False)
    database_type = db.Column(DatabaseTypesSQLAlchemy, nullable=False)
    source_link = db.Column(db.String())
    description = db.Column(db.Text)
    is_archived = db.Column(db.Boolean, default=False, nullable=False)

    # relationships
    fields = db.relationship(
        "Field",
        foreign_keys="Field.resource_name",
        backref="resource",
        cascade="all, delete-orphan",
    )
    relationships = db.relationship(
        "Relationship",
        foreign_keys="Relationship.resource_name",
        backref="resource",
        cascade="all, delete-orphan",
    )
    resource_filter = db.relationship(
        "ResourceFilter",
        foreign_keys="ResourceFilter.resource_name",
        backref="resource",
        cascade="all, delete-orphan",
        uselist=False,
    )

    def __repr__(self):
        return (
            f'<Resource: type="{self.type}" name="{self.name}" '
            + f'app="{self.app}">'
        )
