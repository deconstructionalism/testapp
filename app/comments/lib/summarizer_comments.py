from app.comments.models import Comment, FieldComment, ResourceComment
from app.summarize.models import Field, Resource
from flask import abort


class SummarizerComments:
    """
    Get single comments for resources and fields.
    """

    @staticmethod
    def get_field_comment(
        app_name: str, resource_name: str, field_name: str, comment_id: int
    ) -> Comment:
        """Get a field comment."""

        try:

            comment = Comment.query.filter(
                Comment.field_comment.has(comment_id=comment_id),
                Comment.field_comment.has(
                    FieldComment.field.has(Field.name.endswith(field_name))
                ),
                Comment.field_comment.has(
                    FieldComment.field.has(
                        Field.resource.has(
                            Resource.name.endswith(resource_name)
                        )
                    )
                ),
                Comment.field_comment.has(
                    FieldComment.field.has(
                        Field.resource.has(Resource.app == app_name)
                    )
                ),
            ).first()

            # return failure code if comment is not found
            if not comment:
                abort(
                    404, description=f'field comment "{comment_id}" not found'
                )

            return comment

        except AttributeError:
            abort(404, description=f'field comment "{comment_id}" not found')

    @staticmethod
    def get_resource_comment(
        app_name: str, resource_name: str, comment_id: int
    ) -> Comment:
        """Get a resource comment."""

        try:
            comment = Comment.query.filter(
                Comment.resource_comment.has(comment_id=comment_id),
                Comment.resource_comment.has(
                    ResourceComment.resource.has(
                        Resource.name.endswith(resource_name)
                    )
                ),
                Comment.resource_comment.has(
                    ResourceComment.resource.has(Resource.app == app_name)
                ),
            ).first()

            # return failure code if comment is not found
            if not comment:
                abort(
                    404,
                    description=f'resource comment "{comment_id}" not found',
                )

            return comment

        except AttributeError:
            abort(
                404, description=f'resource comment "{comment_id}" not found'
            )
