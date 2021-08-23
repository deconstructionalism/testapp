from app.lib import BaseModel, db


class Relationship(BaseModel):
    __tablename__ = "relationship"

    # columns
    type = db.Column(db.String(), nullable=False)
    field = db.Column(db.String(), nullable=False, primary_key=True)
    related_field = db.Column(db.String(), nullable=False, primary_key=True)
    description = db.Column(db.Text)

    # references
    resource_name = db.Column(
        db.String(),
        db.ForeignKey("resource.name"),
        nullable=False,
        primary_key=True,
    )
    related_resource_name = db.Column(
        db.String(),
        db.ForeignKey("resource.name"),
        nullable=False,
        primary_key=True,
    )

    # relationships
    resource = db.relationship(
        "Resource",
        back_populates="relationships",
        foreign_keys=[resource_name],
    )
    related_resource = db.relationship(
        "Resource", foreign_keys=[related_resource_name]
    )

    def __repr__(self):
        return (
            f'<Relationship: type="{self.type}" '
            + f'to="{self.related_resource.name}">'
        )
