from app.lib import BaseModel, db


class FieldFilter(BaseModel):
    __tablename__ = "field_filter"

    # columns
    field_name = db.Column(
        db.String(), db.ForeignKey("field.name"), primary_key=True
    )

    # serializer config
    serialize_rules = ("-date_modified",)

    def __repr__(self):
        return f"<FieldFilter field={self.field_name}>"
