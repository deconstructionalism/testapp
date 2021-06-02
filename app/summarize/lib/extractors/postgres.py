from .resource import Field, ForeignKeyField, Meta, Relationship, Resource
from django.db.models.base import ModelBase
from django.db.models.fields import Field as ModelField
from django.db.models.fields.related import RelatedField
from django.db.models.fields.reverse_related import ForeignObjectRel
from re import sub
from typing import List, Union


# HELPER FUNCTIONS


def get_resource_name(resource: ModelBase) -> str:
    """Get the name for a resource."""

    return "{}.{}".format(resource.__module__, resource.__name__)


# MAIN CLASSES


class PGMeta(Meta):
    """Postgres field metadata (singular) concrete class."""

    def __init__(self, meta: Union[str, int, float, bool], name: str) -> None:
        super().__init__(meta, name)


class PGField(Field):
    """
    Postgres field concrete class.

    (see metaclass for method docs)
    """

    @property
    def name(self) -> str:
        return self._value.column

    @property
    def type(self) -> str:
        return self._value.get_internal_type()

    @property
    def metadata(self) -> List[PGMeta]:
        return [
            PGMeta(value, name)
            for name, value in self._value.__dict__.items()
        ]

    def __init__(self, field: ModelField) -> None:
        super().__init__(field)


class PGForeignKeyField(PGField, ForeignKeyField):
    """
    Postgres foreign key field concrete class.

    (see metaclass for method docs)
    """

    @property
    def related_resource(self) -> str:
        return get_resource_name(self._value.related_model)

    @property
    def related_field(self) -> str:
        return PGField(self._value.target_field).name

    def __init__(self, field: RelatedField) -> None:
        super().__init__(field)


class PGVirtualField(Field):
    """
    Postgres virtual field concrete class.

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


class PGRelationship(Relationship):
    """
    Postgres relationship concrete class.

    (see metaclass for method docs)
    """

    @property
    def type(self) -> str:
        return sub("Rel$", "", type(self._value).__name__)

    @property
    def field(self) -> str:
        return PGField(self._value.target_field).name

    @property
    def related_resource(self) -> str:
        return get_resource_name(self._value.related_model)

    @property
    def related_field(self) -> str:
        return PGField(self._value.field).name

    def __init__(self, relationship: ForeignObjectRel) -> None:
        super().__init__(relationship)


class PGResource(Resource):
    """
    Postgres resource concrete class.

    (see metaclass for method docs)
    """

    @property
    def primary_key(self) -> str:
        return PGField(self._value._meta.pk).name

    @property
    def fields(self) -> List[PGField]:
        return [
            PGField(field)
            for field in self._value._meta.get_fields()
            if isinstance(field, ModelField)
        ]

    @property
    def foreign_key_fields(self) -> List[PGForeignKeyField]:
        return [
            PGForeignKeyField(field)
            for field in self._value._meta.get_fields()
            if isinstance(field, RelatedField)
        ]

    @property
    def virtual_fields(self) -> List[PGVirtualField]:
        fields = []

        for name in dir(self._value):
            try:
                value = getattr(self._value, name)

                if isinstance(value, property):
                    fields.append(PGVirtualField(value, name))
            except AttributeError:
                print(f'unable to get virtual "{name}" from {self._value}')

        return fields

    @property
    def relationships(self) -> List[PGRelationship]:
        return [
            PGRelationship(field)
            for field in self._value._meta.get_fields()
            if isinstance(field, ForeignObjectRel)
        ]

    def __init__(self, resource: ModelBase) -> None:
        super().__init__(resource, "postgres")
