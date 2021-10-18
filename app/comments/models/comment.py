from app.lib import BaseModel, db


class Comment(BaseModel):
    __tablename__ = "comment"

    # columns
    filter_by = db.Column(db.String(), unique=True, nullable=False)
    type = db.Column(db.String(), default="field")

    # serializer config
    serialize_rules = ("-date_modified", "-id")

    def __repr__(self):
        return f"<FieldFilter field={self.filter_by}>"
