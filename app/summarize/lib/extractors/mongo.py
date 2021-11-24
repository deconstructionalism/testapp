import re
from app.lib.logger import logger
from app.lib.types import MongoModelType
from app.summarize.lib import DefaultTransformer
from app.summarize.lib.extractors import (
    AbstractField,
    AbstractMetadata,
    AbstractResource,
)
from mongoengine.base import BaseField
from mongoengine.connection import ConnectionFailure
from mongoengine.fields import LazyReferenceField, ReferenceField
from typing import Any, List, Optional, Tuple, Type, Union, get_type_hints

# HELPER FUNCTIONS


def get_resource_name(resource: MongoModelType) -> str:
    """Get the unique name for a resource."""

    return "{}.{}".format(resource.__module__, resource.__name__)


# MONGO FIELD TYPE TRANSFORMER


class MongoFieldTypeTransformer:
    """
    Configure a `DefaultTransformer` instance to get mongo field type
    strings from field data.
    """

    def __full_name(cls: Type) -> str:
        """Get full class name including module path."""

        return "{}.{}".format(cls.__module__, cls.__name__)

    def __document(field: Type, field_type: str) -> Tuple[str, str]:
        """Get field type string for a document reference."""

        referenced_type = MongoFieldTypeTransformer.__full_name(
            field.document_type
        )

        return [f"{field_type}<{referenced_type}>", referenced_type]

    def __field(field: Type, field_type: str) -> Tuple[str, str]:
        """Get field type string for a field reference."""

        referenced_type = (
            "Any"
            if getattr(field, "field", None) is None
            else MongoFieldTypeTransformer.__full_name(field.field.__class__)
        )

        return [f"{field_type}<{referenced_type}>", referenced_type]

    # if you want to parse a `mongoengine` field type in a non-generic way,
    # add a named config here that takes `field` and `field_type` as args and
    # returns an `str`
    types_config = {
        "EmbeddedDocumentField": __document,
        "EmbeddedDocumentListField": (
            lambda field, field_type: MongoFieldTypeTransformer.__document(
                field.field, field_type
            )
        ),
        "ReferenceField": __document,
        "LazyReferenceField": __document,
        "ListField": __field,
        "MapField": __field,
    }

    # create `DefaultTransformer` instance and add all type configurations
    # from `types_config`
    transformer = DefaultTransformer(
        lambda field: field.__class__.__name__,
        lambda field, _: (field.__class__.__name__, None),
    )

    for pair in types_config.items():
        transformer.register(*pair)

    def __call__(self, item: Any) -> Any:
        return MongoFieldTypeTransformer.transformer(item)


# MAIN CLASSES


class MongoMetadata(AbstractMetadata):
    """Mongo field metadata (singular) concrete class."""

    @property
    def name(self):
        return f"{self._field_name}.{self._name}"

    @property
    def value(self):

        # strip memory address if present
        value = re.sub(r" \S+ at 0x[0-9A-Za-z]{9}", "", str(self._value))
        return value

    @property
    def field_name(self):
        return self._field_name

    def __init__(
        self, meta: Union[str, int, float, bool], name: str, field_name: str
    ) -> None:
        super().__init__(meta)
        self._name = name
        self._field_name = field_name


class MongoField(AbstractField):
    """
    Mongo field concrete class.

    (see metaclass for method docs)
    """

    @property
    def name(self) -> str:
        return f"{self._resource_name}.{self._value.name}"

    @property
    def type(self) -> str:
        return self.__transformer(self._value)[0]

    @property
    def resource_name(self) -> None:
        return self._resource_name

    @property
    def related_resource_name(self) -> None:
        return None

    @property
    def is_primary_key(self) -> bool:
        return self.name == self._resource_primary_key

    @property
    def is_virtual(self) -> bool:
        return False

    @property
    def metadata(self) -> List[MongoMetadata]:
        return [
            MongoMetadata(value, name, self.name)
            for name, value in self._value.__dict__.items()
        ]

    def __init__(
        self,
        field: BaseField,
        resource_name: str,
        resource_primary_key: Optional[str] = None,
    ) -> None:
        super().__init__(field)
        self.__transformer = MongoFieldTypeTransformer()
        self._resource_name = resource_name
        self._resource_primary_key = resource_primary_key


class MongoVirtualField(MongoField):
    """
    Mongo virtual field concrete class.

    (see metaclass for method docs)
    """

    @property
    def name(self) -> str:
        return f"{self.resource_name}.{self._name}"

    @property
    def type(self) -> str:
        hints = get_type_hints(self._value.fget)
        return str(hints["return"]) if "return" in hints else "undefined"

    @property
    def is_virtual(self) -> bool:
        return True

    @property
    def metadata(self) -> list:
        return []

    def __init__(
        self, field: property, name: str, resource_name: str
    ) -> None:
        super().__init__(field, resource_name)
        self._name = name


class MongoResource(AbstractResource):
    """
    Mongo resource concrete class.

    (see metaclass for method docs)
    """

    @property
    def app(self) -> str:
        return self._app

    @property
    def primary_key(self) -> str:
        field = next(
            (
                f
                for f in self._value._fields.values()
                if type(f).__name__ == "ObjectIdField"
            ),
            None,
        )

        return field if field is None else field.name

    @property
    def normal_fields(self) -> List[MongoField]:
        return [
            MongoField(field, self.name, self.primary_key)
            for field in self._value._fields.values()
            if not isinstance(field, (LazyReferenceField, ReferenceField))
        ]

    @property
    def virtual_fields(self) -> List[MongoVirtualField]:
        fields = []

        for name in dir(self._value):
            try:
                value = getattr(self._value, name)

                if isinstance(value, property):
                    fields.append(MongoVirtualField(value, name, self.name))
            except AttributeError:
                logger.info(
                    f'unable to get virtual "{name}" from {self._value}'
                )

            except ConnectionFailure:
                # skip any properties that result in getting data from a mongo
                # engine connection as these will invariably fail
                continue

        return fields

    @property
    def relationships(self) -> list:
        return []

    def __init__(self, resource: MongoModelType, app: str) -> None:
        super().__init__(resource, "mongo")
        self._app = app
