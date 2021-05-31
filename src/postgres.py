from collections import defaultdict
from django.db.models.base import ModelBase
from django.db.models.fields import Field
from django.db.models.fields.related import RelatedField
from django.db.models.fields.reverse_related import ForeignObjectRel
from re import sub
from src import resource
from typing import Any, List, Union

# DUMMY FILTER DATA (REPLACE WITH QUERY)

default_included_meta = [
    "null",
    "blank",
    "choices",
    "db_column",
    "db_index",
    "db_tablespace",
    "default",
    "editable",
    "error_messages",
    "help_text",
    "primary_key",
    "unique",
    "unique_for_date",
    "unique_for_month",
    "unique_for_year",
    "verbose_name",
    "validators",
]

included_meta_dict = defaultdict(lambda: default_included_meta)


def default_transform(field: Field, meta_value: Any) -> Any:
    return meta_value


field_transforms = {
    "default": lambda field, meta_value: field.get_default(),
    "validators": lambda field, meta_value: [
        type(v).__name__ for v in meta_value
    ],
}

field_transform_dict = defaultdict(lambda: default_transform)

for k, v in field_transforms.items():
    field_transform_dict[k] = v


# HELPER METHODS


def get_resource_name(resource: ModelBase) -> str:
    """Get the name for a resource."""

    return "{}.{}".format(resource.__module__, resource.__name__)


# MAIN CLASSES


class PGMeta(resource.Meta):
    """Postgres field metadata (singular) concrete class."""

    def __init__(self, meta: Union[str, int, float, bool], name: str) -> None:
        super().__init__(meta, name)


class PGField(resource.Field):
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
        def get_transform_meta_value(field: Field, meta_name: str) -> Any:
            """
            Get meta value from field and transform according to method in
            `field_transform_dict`.
            """

            meta_value = getattr(field, meta_name, None)
            transform = field_transform_dict[meta_name]

            return transform(field, meta_value)

        included_meta = included_meta_dict[type]

        meta = []

        for meta_name in included_meta:
            value = get_transform_meta_value(self._value, meta_name)
            if value not in [None, ""]:
                meta.append(PGMeta(value, meta_name))

        return meta

    def __init__(self, field: Field) -> None:
        super().__init__(field)


class PGForeignKeyField(PGField, resource.ForeignKeyField):

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

    def __init__(self, field: object) -> None:
        super().__init__(field)


class PGVirtualField(resource.Field):

    """
    Postgres virtual field concrete class.

    (see metaclass for method docs)
    """

    @property
    def name(self) -> str:
        return self._name

    @property
    def type(self) -> str:
        return 'virtual'

    @property
    def metadata(self) -> list:
        return []

    def __init__(self, field: property, name: str) -> None:
        super().__init__(field)
        self._name = name


class PGRelationship(resource.Relationship):

    """
    Postgres relationship concrete class.

    (see metaclass for method docs)
    """

    @property
    def type(self) -> str:
        return sub(
            "([a-z])([A-Z])",
            "\\g<1> \\g<2>",
            sub("Rel$", "", type(self._value).__name__),
        )

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


class PGResource(resource.Resource):

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
            if isinstance(field, Field)
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
