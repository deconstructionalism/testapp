from app.filters.lib import generate_filter_routes
from app.filters.models import MetadataFilter, FieldFilter, ResourceFilter
from flask import Blueprint, jsonify

filter_blueprint = Blueprint("filters", __name__, url_prefix="/filters")


@filter_blueprint.route("/", methods=["GET"])
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


generate_filter_routes("field", FieldFilter, filter_blueprint)
generate_filter_routes("metadata", MetadataFilter, filter_blueprint)
generate_filter_routes("resource", ResourceFilter, filter_blueprint)
