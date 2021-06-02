import os
import sys
from django.apps import apps
from django.db.models.base import ModelBase
from importlib.util import (
    spec_from_file_location,
    module_from_spec,
)
from inspect import isclass
from mongoengine.base import BaseDocument
from mongoengine.document import MapReduceDocument
from types import ModuleType
from typing import List, Union

# use `django` settings from `backend` app inside of `marshall`
sys.path.append("marshall/backend")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")

# model class types to include in return for `mongo_models` property in
# `MarshallModels` instance
MONGO_DOCUMENT_CLASSES = [BaseDocument, MapReduceDocument]

# cannot use unpack operator below Python v3.10 to avoid duplication of
# `MONGO_DOCUMENT_CLASSES` contents, so the union of return types needs to be
# specified explicitly
MongoModelType = Union[BaseDocument, MapReduceDocument]


def load_init_only(path_to_module: str) -> ModuleType:
    """Load a module's `__init__.py` file only."""

    path = os.path.join(path_to_module, "__init__.py")
    spec = spec_from_file_location(path_to_module, path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)

    return module


class MarshallModels:
    """Get "web", "dataparty" and "mongo" models from `marshall` app."""

    @staticmethod
    def __app_models(app_name: str) -> List[ModelBase]:
        """Load app models from django instance."""

        return list(apps.get_app_config(app_name).get_models())

    @staticmethod
    def __mongo_models() -> List[MongoModelType]:
        """Load mongo models located in 'marshall/backend/web/mongo'."""

        mongo_module = load_init_only("marshall/backend/web/mongo")

        def is_document_class(obj):
            """Check if object is a subclass of a mongo document class."""

            if not isclass(obj):
                return False
            return any([issubclass(obj, c) for c in MONGO_DOCUMENT_CLASSES])

        mongo_models = [
            model
            for model in mongo_module.__dict__.values()
            if is_document_class(model)
        ]

        return mongo_models

    def __init__(self) -> None:
        # use a fresh `django` instance per instantiation
        self.django = __import__("django")
        self.django.setup()
        self.web = MarshallModels.__app_models("web")
        self.dataparty = MarshallModels.__app_models("dataparty")
        self.mongo = self.__mongo_models()
