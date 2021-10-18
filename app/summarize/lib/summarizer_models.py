from app.lib.base_model import NamedBaseModel
from app.filters.models import FieldFilter, MetadataFilter, ResourceFilter
from app.summarize.models import Field, Resource
from app.summarize.lib.extractors import (
    SummarizerField,
    SummarizerMetadata,
    SummarizerResource,
)
from flask import abort
from re import search
from typing import List, Union


# HELPER FUNCTIONS


def filter_models(
    models: List[NamedBaseModel],
    filter_class: Union[FieldFilter, MetadataFilter, ResourceFilter],
):
    """
    For a list of named models, filter out any models who have names matching
    the regex filters in a given filter class.
    """

    filters = filter_class.query.all()

    return [
        model
        for model in models
        if not any([search(f.filter_by, model.name) for f in filters])
    ]


# EXTRACTOR CLASS OVERRIDES


class SummarizerFieldFiltered(SummarizerField):
    """
    Override `SummarizerField` class with filtered metadata.
    """

    @property
    def metadata(self) -> List[SummarizerMetadata]:
        return filter_models(super().metadata, MetadataFilter)

    def __init__(self, field: Field) -> None:
        super().__init__(field)


class SummarizerResourceFiltered(SummarizerResource):
    """
    Override `SummarizerResource` class with filtered fields.
    """

    @property
    def fields(self) -> List[SummarizerFieldFiltered]:
        _fields = [SummarizerFieldFiltered(f) for f in self._value.fields]
        return filter_models(_fields, FieldFilter)

    def __init__(self, resource: Resource) -> None:
        super().__init__(resource)


# SUMMARIZER CLASS


class SummarizerModels:
    """
    Get app, resource, and field data from summarizer database in `dict`
    format. Models are filtered according to filters data.
    """

    @staticmethod
    def get_all_resources() -> List[dict]:
        """Get all resources."""

        resources = filter_models(Resource.query.all(), ResourceFilter)

        return [
            SummarizerResourceFiltered(resource).__dict__
            for resource in resources
        ]

    @staticmethod
    def get_app_resources(app_name: str) -> List[dict]:
        """Get all resources for a given app."""

        resources = filter_models(
            Resource.query.filter_by(app=app_name), ResourceFilter
        )

        # return failure code if no resources exist for app
        if not resources:
            abort(404, description=f'app "{app_name}" not found')

        return [
            SummarizerResourceFiltered(resource).__dict__
            for resource in resources
        ]

    @staticmethod
    def get_resource(app_name: str, resource_name: str) -> dict:
        """Get a resource from an app."""

        try:
            resources = filter_models(
                Resource.query.filter(
                    (Resource.app == app_name)
                    & (Resource.name.endswith(f".{resource_name}"))
                ),
                ResourceFilter,
            )

            # since resource_name should be unique, this should only ever
            # return one resource
            resource = resources[0]

            # return failure code if resource is not found
            if not resource:
                abort(
                    404, description=f'resource "{resource_name}" not found'
                )

            return SummarizerResourceFiltered(resource).__dict__

        except AttributeError:
            abort(404, description=f'resource "{resource_name}" not found')

    @staticmethod
    def get_field(app_name: str, resource_name: str, field_name: str) -> dict:
        """Get a field from an app model."""

        try:

            # get the named resource
            resource = SummarizerModels.get_resource(app_name, resource_name)

            # extract the field from the named resource if it exists
            field = next(
                (
                    field
                    for field in resource["fields"]
                    if field["name"].endswith(f".{field_name}")
                ),
                None,
            )

            # return failure code if field is not found
            if not field:
                abort(404, description=f'field "{field_name}" not found')

            return field

        except AttributeError:
            abort(404, description=f'field "{field_name}" not found')
