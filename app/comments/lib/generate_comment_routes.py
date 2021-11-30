from app.comments.lib.summarizer_comments import SummarizerComments
from app.comments.models import Comment, FieldComment, ResourceComment
from app.database import db
from app.lib import validate_body
from app.summarize.lib.summarizer_models import SummarizerModels
from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError
from typing_extensions import Literal

root_route = "/<app_name>/<resource_name>"


def generate_comment_routes(
    entity: Literal["field", "resource"], blueprint: Blueprint,
) -> None:
    """
    Helper function to generate get and patch routes to view and toggle filters
    for a given entity type.
    """

    # determine route settings based on `entity` value
    index_route = None
    item_route = None
    comment_model = None
    get_parent = None
    get_linked_comment = None

    if entity is "field":
        index_route = "/<app_name>/<resource_name>/<field_name>"
        item_route = f"{index_route}/<int:comment_id>"
        comment_model = FieldComment
        get_parent = SummarizerModels.get_field
        get_linked_comment = SummarizerComments.get_field_comment
    else:
        index_route = "/<app_name>/<resource_name>"
        item_route = f"{index_route}/<int:comment_id>"
        comment_model = ResourceComment
        get_parent = SummarizerModels.get_resource
        get_linked_comment = SummarizerComments.get_resource_comment

    @blueprint.route(
        item_route, methods=["GET"], endpoint=f"show_{entity}_comment"
    )
    def show_comment(**kwargs):
        comment = get_linked_comment(**kwargs)

        return comment.to_dict(), 200

    @blueprint.route(
        index_route, methods=["GET"], endpoint=f"index_{entity}_comments"
    )
    def index_comments(**kwargs):
        parent = get_parent(**kwargs)

        return jsonify(parent["comments"])

    @blueprint.route(
        index_route, methods=["POST"], endpoint=f"create_{entity}_comment"
    )
    @validate_body(
        {
            "type": "object",
            "properties": {
                "content": {"type": "string"},
                "email": {"type": "string"},
            },
            "required": ["content", "email"],
            "additionalProperties": False,
        }
    )
    def create_comment(**kwargs):
        body = request.get_json()
        content = body["content"]
        email = body["email"]

        parent = get_parent(**kwargs)

        try:
            new_comment = Comment(content=content, email=email)
            db.session.add(new_comment)
            db.session.flush()

            linked_kwargs = {"comment_id": new_comment.id}
            linked_kwargs[f"{entity}_name"] = parent["name"]

            new_linked_comment = comment_model(**linked_kwargs)
            db.session.add(new_linked_comment)
            db.session.flush()
            db.session.commit()

            return new_comment.to_dict(), 201
        except IntegrityError as e:
            return {"status": "failure", "error": e.__str__()}, 400

    @blueprint.route(
        item_route, methods=["PATCH"], endpoint=f"update_{entity}_comment"
    )
    @validate_body(
        {
            "type": "object",
            "properties": {"content": {"type": "string"}},
            "additionalProperties": False,
        }
    )
    def update_comment(**kwargs):
        body = request.get_json()

        comment = get_linked_comment(**kwargs)

        try:
            comment.content = body["content"]
            db.session.commit()

            return comment.to_dict(), 200
        except IntegrityError as e:
            return {"status": "failure", "error": e.__str__()}, 400

    @blueprint.route(
        item_route, methods=["DELETE"], endpoint=f"delete_{entity}_comment"
    )
    def delete_comment(**kwargs):
        comment = get_linked_comment(**kwargs)

        try:
            db.session.delete(comment)
            db.session.commit()
            return (
                {
                    "status": "success",
                    "data": {"message": f"{entity} comment deleted"},
                },
                200,
            )
        except IntegrityError as e:
            return {"status": "failure", "error": e.__str__()}, 400
