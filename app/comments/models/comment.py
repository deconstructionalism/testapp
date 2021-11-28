from app.lib import BaseModel, db


class Comment(BaseModel):
    __tablename__ = "comment"

    # columns
    content = db.Column(db.Text(), nullable=False)
    email = db.Column(db.String(), default="field", nullable=False)

    # relationships
    field_comment = db.relationship(
        "FieldComment",
        foreign_keys="FieldComment.comment_id",
        backref="comment",
        cascade="all, delete-orphan",
        uselist=False,
    )
    resource_comment = db.relationship(
        "ResourceComment",
        foreign_keys="ResourceComment.comment_id",
        backref="comment",
        cascade="all, delete-orphan",
        uselist=False,
    )

    # serializer config
    serialize_rules = ("-field_comment", "-resource_comment")

    def __repr__(self):
        return f"<Comment email={self.email}>"
