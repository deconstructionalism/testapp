import enum
from mongoengine.base import BaseDocument
from mongoengine.document import MapReduceDocument
from typing_extensions import Literal
from typing import Union
from sqlalchemy import Enum


class _DatabaseTypesEnum(enum.Enum):
    postgres = "postgres"
    mongo = "mongo"


DatabaseTypes = Literal[_DatabaseTypesEnum.postgres, _DatabaseTypesEnum.mongo]

DatabaseTypesSQLAlchemy = Enum(_DatabaseTypesEnum)

# model class types to include in return for `mongo_models` property in
# `MarshallModels` instance
MongoDocumentClasses = [BaseDocument, MapReduceDocument]

# cannot use unpack operator below Python v3.10 to avoid duplication of
# `MongoDocumentClasses` contents, so the union of return types needs to be
# specified explicitly
MongoModelType = Union[BaseDocument, MapReduceDocument]
