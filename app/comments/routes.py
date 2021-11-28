from app.comments.lib.generate_comment_routes import generate_comment_routes
from flask import Blueprint

comment_blueprint = Blueprint("comments", __name__, url_prefix="/comments")

generate_comment_routes("field", comment_blueprint)
generate_comment_routes("resource", comment_blueprint)
