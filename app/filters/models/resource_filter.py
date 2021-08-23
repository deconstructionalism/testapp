from app.lib import BaseModel, db


class ResourceFilter(BaseModel):
    __tablename__ = "resource_filter"

    # columns
    resource_name = db.Column(
        db.String(), db.ForeignKey("resource.name"), primary_key=True
    )

    # serializer config
    serialize_rules = ("-date_modified",)

    def __repr__(self):
        return f"<ResourceFilter resource={self.resource_name}>"
