from ..default_transformer import DefaultTransformer, Transformer
from .resource import Field, ForeignKeyField, Meta, Resource
from app.lib.types import MongoModelType
from mongoengine.base import BaseField
from mongoengine.fields import LazyReferenceField, ReferenceField
from typing import List, Type, Union


# HELPER FUNCTIONS


def get_resource_name(resource: MongoModelType) -> str:
    """Get the name for a resource."""

    return "{}.{}".format(resource.__module__, resource.__name__)


# MONGO FIELD TRANSFORMER CONFIG


def get_full_name(cls: Type) -> str:
    """Get full class name including module path."""

    return "{}.{}".format(cls.__module__, cls.__name__)


def document_string(field: Type, field_type: str) -> str:
    """Get field type string for a document reference."""

    return f"{field_type.capitalize()}<{get_full_name(field.document_type)}>"


def nullable_field_string(field: Type, field_type: str) -> str:
    """Get field type string for a field reference."""
    sub_field_type = (
        "Any"
        if getattr(field, "field", None) is None
        else get_full_name(field.field.__class__)
    )

    return f"{field_type.capitalize()}<{sub_field_type}>"


mongo_extractor_config = {
    "EmbeddedDocumentField": document_string,
    "EmbeddedDocumentListField": lambda field, field_type: document_string(
        field.field, field_type
    ),
    "ReferenceField": document_string,
    "LazyReferenceField": document_string,
    "ListField": nullable_field_string,
    "MapField": nullable_field_string,
}


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

    @staticmethod
    def __init_type_transformer() -> Transformer:
        """
        Set up default transfomer for rich type string with all
        transformations in `mongo_extractor_config`.
        """

        transformer = DefaultTransformer(
            lambda field: field.__class__.__name__,
            lambda field, _: field.__class__.__name__,
        )

        for pair in mongo_extractor_config.items():
            transformer.register(*pair)

        return transformer

    @property
    def name(self) -> str:
        return self._value.name

    @property
    def type(self) -> str:
        return self.__type_transformer(self._value)

    @property
    def metadata(self) -> List[MongoMeta]:
        return [
            MongoMeta(value, name)
            for name, value in self._value.__dict__.items()
        ]

    def __init__(self, field: BaseField) -> None:
        super().__init__(field)
        self.__type_transformer = MongoField.__init_type_transformer()


class MongoForeignKeyField(MongoField, ForeignKeyField):
    """
    Mongo foreign key field concrete class.

    (see metaclass for method docs)
    """

    @property
    def related_resource(self) -> str:
        return get_resource_name(self._value.document_type)

    @property
    def related_field(self) -> str:
        field = next(
            (
                f
                for f in self._value.document_type._fields.values()
                if f.__class__.__name__ == "ObjectIdField"
            ),
            None,
        )

        return field if field is None else MongoField(field).name

    def __init__(self, field: BaseField) -> None:
        super().__init__(field)


class MongoVirtualField(Field):
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
            (f for f in self.fields if f.type == "ObjectIdField"), None
        )

        return field if field is None else field.name

    @property
    def fields(self) -> List[MongoField]:
        return [
            MongoField(field)
            for field in self._value._fields.values()
            if not isinstance(field, (LazyReferenceField, ReferenceField))
        ]

    @property
    def foreign_key_fields(self) -> list:
        return [
            MongoForeignKeyField(field)
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
