from app.summarize.models import Field, Resource
from app.summarize.lib.extractors import (
    SummarizerResource,
    SummarizerField,
)
from flask import abort
from typing import List


class SummarizerModels:
    """
    Get app, resource, and field data from summarizer database in `dict`
    format.
    """

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

            return SummarizerResource(model).__dict__
        except AttributeError:
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
        except AttributeError:
            abort(404, description=f'field "{field_name}" not found')
