from app.lib import BaseModel, db


class ResourceComment(BaseModel):
    __tablename__ = "resource_comment"

    # relationships
    resource_name = db.Column(
        db.String(), db.ForeignKey("resource.name"), nullable=False
    )
    comment_id = db.Column(
        db.Integer, db.ForeignKey("comment.id"), nullable=False
    )

    # serializer config
    serialize_rules = ("-date_modified", "-id")

    def __repr__(self):
        return f"<ResourceComment resource={self.resource_name}>"
