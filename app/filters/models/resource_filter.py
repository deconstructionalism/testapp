from enum import unique
from app.lib import BaseModel, db


class ResourceFilter(BaseModel):
    __tablename__ = "resource_filter"

    # columns
    filter_by = db.Column(db.String(), unique=True, nullable=False)
    type = db.Column(db.String(), default="resource")

    # serializer config
    serialize_rules = ("-date_modified", "-id")

    def __repr__(self):
        return f"<ResourceFilter resource={self.filter_by}>"
