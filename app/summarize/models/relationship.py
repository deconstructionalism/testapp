from app.lib import NamedBaseModel, db


class Relationship(NamedBaseModel):
    __tablename__ = "relationship"

    # columns
    type = db.Column(db.String(), nullable=False)
    description = db.Column(db.Text)

    # references
    field_name = db.Column(
        db.String(),
        # db.ForeignKey("field.name"),
        nullable=False,
    )
    related_field_name = db.Column(
        db.String(),
        # db.ForeignKey("field.name"),
        nullable=False,
    )
    resource_name = db.Column(
        db.String(), db.ForeignKey("resource.name"), nullable=False
    )
    related_resource_name = db.Column(
        db.String(),
        # db.ForeignKey("resource.name"),
        nullable=False,
    )

    def __repr__(self):
        return (
            f'<Relationship: type="{self.type}" '
            + f'to="{self.related_resource.name}">'
        )
