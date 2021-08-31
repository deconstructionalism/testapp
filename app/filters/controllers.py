from app.filters.lib.generate_filter_routes import generate_filter_routes
from app.filters.models import MetadataFilter, FieldFilter, ResourceFilter
from flask import Blueprint, jsonify

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


generate_filter_routes("field", FieldFilter, filters)
generate_filter_routes("metadata", MetadataFilter, filters)
generate_filter_routes("resource", ResourceFilter, filters)
