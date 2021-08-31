# from flask import abort, Blueprint, jsonify
# from .lib import MarshallModels
# from typing import List
# # from app.summarize.lib.differencer import update_database


# summarize = Blueprint("summarize", __name__, url_prefix="/summarize")
# model_controller = MarshallModels()


# class Models:
#     """Utility class for getting model data."""

#     models = {
#         "web": [
#             model.__dict__ for model in model_controller.get_models("web")
#         ],
#         "mongo": [
#             model.__dict__ for model in model_controller.get_models("mongo")
#         ],
#         "dataparty": [
#             model.__dict__
#             for model in model_controller.get_models("dataparty")
#         ],
#     }

#     def get_all_models() -> List[dict]:
#         """Get all models."""

#         return [model for app in Models.models.values() for model in app]

#     def get_app_models(app_name: str) -> List[dict]:
#         """Get all models for a given app."""

#         try:
#             app_models = Models.models[app_name]
#             return app_models
#         except KeyError:
#             abort(404, description=f'app "{app_name}" not found')

#     def get_model(app_name: str, model_name: str) -> dict:
#         """Get a model from an app."""

#         app_models = Models.get_app_models(app_name)
#         try:
#             model = next(
#                 (m for m in app_models if m["name"].endswith(model_name)),
#             )
#             return model
#         except StopIteration:
#             abort(404, description=f'model "{model_name}" not found')

#     def get_field(app_name: str, model_name: str, field_name: str) -> dict:
#         """Get a field from an app model."""

#         model = Models.get_model(app_name, model_name)
#         try:
#             field = next(
#                 (f for f in model["fields"] if f["name"] == field_name),
#             )
#             return field
#         except StopIteration:
#             abort(404, description=f'field "{field_name}" not found')


# @summarize.route("/", methods=["GET"])
# def index_models():
#     return jsonify(Models.get_all_models())


# @summarize.route("/<app_name>", methods=["GET"])
# def index_app_models(app_name: str):
#     app_models = Models.get_app_models(app_name)

#     return jsonify(app_models)


# @summarize.route("/<app_name>/<model_name>", methods=["GET"])
# def show_model(app_name: str, model_name: str):
#     model = Models.get_model(app_name, model_name)

#     return jsonify(model)


# @summarize.route("/<app_name>/<model_name>/<field_name>", methods=["GET"])
# def show_field(app_name: str, model_name: str, field_name: str):
#     field = Models.get_field(app_name, model_name, field_name)

#     return jsonify(field)


# # @summarize.route("/refresh", methods=["POST"])
# # def refresh_models():
# #     update_database()

# #     return ({"status": "success", "data": "database updated"}, 200)


from app.summarize.models.resource import Resource
from app.summarize.models.field import Field
from app.summarize.lib.extractors.summarizer import (
    SummarizerResource,
    SummarizerField,
)
from flask import abort, Blueprint, jsonify
from typing import List

from app.summarize.lib.differencer import update_database


summarize = Blueprint("summarize", __name__, url_prefix="/summarize")


class Models:
    """Utility class for getting model data."""

    def get_all_models() -> List[dict]:
        """Get all models."""

        return [
            SummarizerResource(model).__dict__
            for model in Resource.query.all()
        ]

    def get_app_models(app_name: str) -> List[dict]:
        """Get all models for a given app."""

        app_models = [
            SummarizerResource(model).__dict__
            for model in Resource.query.filter_by(app=app_name)
        ]

        if len(app_models) == 0:
            abort(404, description=f'app "{app_name}" not found')

        return app_models

    def get_model(app_name: str, model_name: str) -> dict:
        """Get a model from an app."""

        try:
            model = Resource.query.filter(
                (Resource.app == app_name)
                & (Resource.name.endswith(model_name))
            ).first()

            print(model)
            return SummarizerResource(model).__dict__
        except AttributeError as e:
            print(e)
            abort(404, description=f'model "{model_name}" not found')

    def get_field(app_name: str, model_name: str, field_name: str) -> dict:
        """Get a field from an app model."""

        try:
            field = Field.query.filter(
                (Field.name == field_name)
                & (Field.resource.app == app_name)
                & (Field.resource.name.endswith(model_name))
            ).first()
            return SummarizerField(field).__dict__
        except StopIteration:
            abort(404, description=f'field "{field_name}" not found')


@summarize.route("/", methods=["GET"])
def index_models():
    return jsonify(Models.get_all_models())


@summarize.route("/<app_name>", methods=["GET"])
def index_app_models(app_name: str):
    app_models = Models.get_app_models(app_name)

    return jsonify(app_models)


@summarize.route("/<app_name>/<model_name>", methods=["GET"])
def show_model(app_name: str, model_name: str):
    model = Models.get_model(app_name, model_name)

    return jsonify(model)


@summarize.route("/<app_name>/<model_name>/<field_name>", methods=["GET"])
def show_field(app_name: str, model_name: str, field_name: str):
    field = Models.get_field(app_name, model_name, field_name)

    return jsonify(field)


@summarize.route("/refresh", methods=["POST"])
def refresh_models():
    update_database()

    return ({"status": "success", "data": "database updated"}, 200)
