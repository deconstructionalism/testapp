import os
import sys
from .extractors import MongoResource, PGResource
from app.lib.types import MongoDocumentClasses, MongoModelType
from django.apps import apps
from django.db.models.base import ModelBase
from importlib.util import (
    spec_from_file_location,
    module_from_spec,
)
from inspect import isclass
from types import ModuleType
from typing import List

# use `django` settings from `backend` app inside of `marshall`
sys.path.append("marshall/backend")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")


def load_init_only(path_to_module: str) -> ModuleType:
    """Load a module's `__init__.py` file only."""

    path = os.path.join(path_to_module, "__init__.py")
    spec = spec_from_file_location(path_to_module, path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)

    return module


class MarshallModels:
    """Get postgres and "mongo" models from `marshall` app."""

    @staticmethod
    def __app_models(app: str) -> List[ModelBase]:
        """Load app models from django instance."""

        return list(apps.get_app_config(app).get_models())

    @staticmethod
    def __mongo_models() -> List[MongoModelType]:
        """Load mongo models located in 'marshall/backend/web/mongo'."""

        mongo_module = load_init_only("marshall/backend/web/mongo")

        def is_document_class(obj):
            """Check if object is a subclass of a mongo document class."""

            if not isclass(obj):
                return False
            return any([issubclass(obj, c) for c in MongoDocumentClasses])

        mongo_models = [
            model
            for model in mongo_module.__dict__.values()
            if is_document_class(model)
        ]

        return mongo_models

    @classmethod
    def get_models(cls, app: str) -> List[PGResource]:
        """Get models from `marshall` by app name."""

        if app == "mongo":
            return [
                MongoResource(model, app) for model in cls.__mongo_models()
            ]

        return [PGResource(model, app) for model in cls.__app_models(app)]

    def __init__(self) -> None:
        # use a fresh `django` instance per instantiation
        django = __import__("django")
        django.setup()
