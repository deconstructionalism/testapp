from os import stat
from ..default_transformer import DefaultTransformer
from .resource import Field, Meta, Resource
from app.lib.types import MongoModelType
from mongoengine.base import BaseField
from mongoengine.fields import LazyReferenceField, ReferenceField
from typing import Any, List, Optional, Tuple, Type, Union
from typing_extensions import Literal


# HELPER FUNCTIONS


def get_resource_name(resource: MongoModelType) -> str:
    """Get the name for a resource."""

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


class MongoMeta(Meta):
    """Mongo field metadata (singular) concrete class."""

    def __init__(self, meta: Union[str, int, float, bool], name: str) -> None:
        super().__init__(meta, name)


class MongoField(Field):
    """
    Mongo field concrete class.

    (see metaclass for method docs)
    """

    @property
    def name(self) -> str:
        return self._value.name

    @property
    def type(self) -> str:
        return self.__transformer(self._value)[0]

    @property
    def foreign_resource_name(self) -> None:
        return None

    @property
    def is_primary_key(self) -> bool:
        return self.name == self.__resource_primary_key

    @property
    def is_virtual(self) -> bool:
        return False

    @property
    def metadata(self) -> List[MongoMeta]:
        return [
            MongoMeta(value, name)
            for name, value in self._value.__dict__.items()
        ]

    def __init__(
        self, field: BaseField, resource_primary_key: Optional[str] = None
    ) -> None:
        super().__init__(field)
        self.__transformer = MongoFieldTypeTransformer()
        self.__resource_primary_key = resource_primary_key


class MongoForeignKeyField(MongoField):
    """
    Mongo foreign key field concrete class.

    (see metaclass for method docs)
    """

    @property
    def foreign_resource_name(self) -> None:
        return self.__transformer(self._value)[1]

    def __init__(
        self, field: BaseField, resource_primary_key: Optional[str]
    ) -> None:
        super().__init__(field, resource_primary_key)


class MongoVirtualField(MongoField):
    """
    Mongo virtual field concrete class.

    (see metaclass for method docs)
    """

    @property
    def name(self) -> str:
        return self._name

    @property
    def type(self) -> str:
        return "virtual"

    @property
    def is_virtual(self) -> bool:
        return True

    @property
    def metadata(self) -> list:
        return []

    def __init__(self, field: property, name: str) -> None:
        super().__init__(field)
        self._name = name


class MongoResource(Resource):
    """
    Mongo resource concrete class.

    (see metaclass for method docs)
    """

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
    def fields(self) -> List[MongoField]:
        return [
            MongoField(field, self.primary_key)
            for field in self._value._fields.values()
            if not isinstance(field, (LazyReferenceField, ReferenceField))
        ]

    @property
    def foreign_key_fields(self) -> list:
        return [
            MongoField(field, self.primary_key)
            for field in self._value._fields.values()
            if isinstance(field, (LazyReferenceField, ReferenceField))
        ]

    @property
    def virtual_fields(self) -> List[MongoVirtualField]:
        fields = []

        for name in dir(self._value):
            try:

                # skip `objects` key which is a `mongoengine.queryset.QuerySet`
                # instance that will slow down the iteration by querying
                # the DB needlessly
                if name == "objects":
                    continue

                value = getattr(self._value, name)

                if isinstance(value, property):
                    fields.append(MongoVirtualField(value, name))
            except AttributeError:
                print(f'unable to get virtual "{name}" from {self._value}')

        return fields

    @property
    def relationships(self) -> list:
        return []

    def __init__(self, resource: MongoModelType) -> None:
        super().__init__(resource, "mongo")
