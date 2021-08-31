from app.lib.base_model import BaseModel
from app.database import db
from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError


def generate_filter_routes(
    entity: str,
    filter_model: BaseModel,
    primary_key: str,
    blueprint: Blueprint,
) -> None:
    """
    Helper function to generate get and patch routes to view and toggle filters
    for a given entity type.
    """
    @blueprint.route(
        f"/{entity}", methods=["GET"], endpoint=f"index_{entity}"
    )
    def index_filters():
        filters = [f.to_dict() for f in filter_model.query.all()]

        return jsonify(filters)

    @blueprint.route(
        f"/{entity}", methods=["PATCH"], endpoint=f"toggle_{entity}"
    )
    def toggle_filter():
        data = request.get_json()

        # check that body request data is valid
        try:
            index = data[primary_key]
        except KeyError:
            return (
                {"status": "fail", "data": {"expected keys": [primary_key]}},
                400,
            )

        # retreive the filter if it exists
        filter = filter_model.query.get(index)

        # delete the filter if it already exists
        if filter:
            db.session.delete(filter)
            db.session.commit()
            return (
                {"status": "success", "data": f"removed {entity} filter"},
                200,
            )
        # create the filter if it already exists, and handle integrity errors
        # if entity primary key reference is non-existant within the database
        else:
            try:
                data = {}
                data[primary_key] = index
                new_filter = filter_model(**data)
                db.session.add(new_filter)
                db.session.commit()
                return (
                    {"status": "success", "data": f"added {entity} filter"},
                    201,
                )
            except IntegrityError as e:
                return {"status": "failure", "error": e.__str__()}, 400
