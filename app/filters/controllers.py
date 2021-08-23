from app.lib.base_model import BaseModel
from app.filters.models import MetadataFilter, FieldFilter, ResourceFilter
from app.database import db
from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError

filters = Blueprint("filters", __name__, url_prefix="/filters")


@filters.route("/", methods=["GET"])
def index():
    filters = [
        f.to_dict()
        for f in [
            *FieldFilter.query.all(),
            *MetadataFilter.query.all(),
            *ResourceFilter.query.all(),
        ]
    ]

    return jsonify(filters)


def generate_filter_routes(
    entity_name: str, filter_model: BaseModel, primary_key: str
) -> None:
    @filters.route(
        f"/{entity_name}", methods=["GET"], endpoint=f"index_{entity_name}"
    )
    def index_filters():
        filters = [f.to_dict() for f in filter_model.query.all()]

        return jsonify(filters)

    @filters.route(
        f"/{entity_name}", methods=["PATCH"], endpoint=f"toggle_{entity_name}"
    )
    def toggle_filter():
        data = request.get_json()

        try:
            index = data[primary_key]
        except KeyError:
            return (
                {"status": "fail", "data": {"expected keys": [primary_key]},},
                400,
            )

        filter = filter_model.query.get(index)

        if filter:
            db.session.delete(filter)
            db.session.commit()
            return (
                {
                    "status": "success",
                    "data": f"removed {entity_name} filter",
                },
                200,
            )
        else:
            try:
                data = {}
                data[primary_key] = index
                new_filter = filter_model(**data)
                db.session.add(new_filter)
                db.session.commit()
                return (
                    {
                        "status": "success",
                        "data": f"added {entity_name} filter",
                    },
                    201,
                )
            except IntegrityError as e:
                return {"status": "failure", "error": e.__str__()}, 400


generate_filter_routes("field", FieldFilter, "field_name")
generate_filter_routes("metadata", MetadataFilter, "metadata_name")
generate_filter_routes("resource", ResourceFilter, "resource_name")
