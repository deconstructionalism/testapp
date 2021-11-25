from app.comments import Comment, FieldComment
from app.database import db
from app.lib import validate_body
from app.summarize.lib import SummarizerModels
from app.summarize.models.field import Field
from flask import Blueprint, request
from flask.json import jsonify
from sqlalchemy.exc import IntegrityError

comments = Blueprint("comments", __name__)


@comments.route(
    "/<app_name>/<resource_name>/<field_name>/comment/<int:comment_id>",
    methods=["GET"],
)
def show_field_comment(
    app_name: str, resource_name: str, field_name: str, comment_id: int
):
    field_comment = SummarizerModels.get_field_comment(
        app_name, resource_name, field_name, comment_id
    )

    return field_comment.comment.to_dict(), 200


@comments.route(
    "/<app_name>/<resource_name>/<field_name>/comment", methods=["GET"],
)
def index_field_comments(app_name: str, resource_name: str, field_name: str):
    field = SummarizerModels.get_field(app_name, resource_name, field_name)

    comments = [
        f_comment.comment.to_dict() for f_comment in field["comments"]
    ]

    return jsonify(comments)


@comments.route(
    "/<app_name>/<resource_name>/<field_name>/comment", methods=["POST"]
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
def create_field_comment(app_name: str, resource_name: str, field_name: str):
    body = request.get_json()
    content = body["content"]
    email = body["email"]

    field = SummarizerModels.get_field(app_name, resource_name, field_name)

    try:
        new_comment = Comment(content=content, email=email)
        db.session.add(new_comment)
        db.session.flush()

        new_field_comment = FieldComment(
            field_name=field["name"], comment_id=new_comment.id
        )
        db.session.add(new_field_comment)
        db.session.flush()
        db.session.commit()

        return new_comment.to_dict(), 201
    except IntegrityError as e:
        return {"status": "failure", "error": e.__str__()}, 400


@comments.route(
    "/<app_name>/<resource_name>/<field_name>/comment/<int:comment_id>",
    methods=["PATCH"],
)
@validate_body(
    {
        "type": "object",
        "properties": {"content": {"type": "string"}},
        "additionalProperties": False,
    }
)
def update_field_comment(
    app_name: str, resource_name: str, field_name: str, comment_id: int
):
    body = request.get_json()

    field_comment = SummarizerModels.get_field_comment(
        app_name, resource_name, field_name, comment_id
    )

    try:
        field_comment.comment.content = body["content"]
        db.session.commit()

        return field_comment.comment.to_dict(), 200
    except IntegrityError as e:
        return {"status": "failure", "error": e.__str__()}, 400


@comments.route(
    "/<app_name>/<resource_name>/<field_name>/comment/<int:comment_id>",
    methods=["DELETE"],
)
def delete_field_comment(
    app_name: str, resource_name: str, field_name: str, comment_id: int
):
    field_comment = SummarizerModels.get_field_comment(
        app_name, resource_name, field_name, comment_id
    )

    try:
        db.session.delete(field_comment.comment)
        db.session.commit()
        return (
            {
                "status": "success",
                "data": {"message": "field comment deleted"},
            },
            200,
        )
    except IntegrityError as e:
        return {"status": "failure", "error": e.__str__()}, 400
