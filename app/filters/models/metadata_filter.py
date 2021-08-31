from app.lib import BaseModel, db


class MetadataFilter(BaseModel):
    __tablename__ = "metadata_filter"

    # columns
    metadata_name = db.Column(
        db.String(), db.ForeignKey("metadata.name"), unique=True
    )

    # serializer config
    serialize_rules = ("-date_modified",)

    def __repr__(self):
        return f"<MetadataFilter metadata={self.metadata_name}>"
