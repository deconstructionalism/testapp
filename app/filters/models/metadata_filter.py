from app.lib import BaseModel, db


class MetadataFilter(BaseModel):
    __tablename__ = "metadata_filter"

    # columns
    filter_by = db.Column(db.String(), unique=True, nullable=False)
    type = db.Column(db.String(), default="metadata")

    # serializer config
    serialize_rules = ("-date_modified", "-id")

    def __repr__(self):
        return f"<MetadataFilter metadata={self.filter_by}>"
