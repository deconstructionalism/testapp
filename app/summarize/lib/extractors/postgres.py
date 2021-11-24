from app.lib.logger import logger
from app.summarize.lib.extractors import (
    AbstractField,
    AbstractMetadata,
    AbstractRelationship,
    AbstractResource,
)
from django.db.models.base import ModelBase
from django.db.models.fields import Field as ModelField
from django.db.models.fields.related import RelatedField
from django.db.models.fields.reverse_related import ForeignObjectRel
from re import sub
from typing import List, Optional, Union, get_type_hints


# HELPER FUNCTIONS


def get_resource_name(resource: ModelBase) -> str:
    """Get the unique name for a resource."""

    return "{}.{}".format(resource.__module__, resource.__name__)


# MAIN CLASSES


class PGMetadata(AbstractMetadata):
    """Postgres field metadata (singular) concrete class."""

    @property
    def name(self):
        return f"{self._field_name}.{self._name}"

    @property
    def value(self):

        # strip memory address if present
        value = sub(r" \S+ at 0x[0-9A-Za-z]{9}", "", str(self._value))
        return value

    @property
    def field_name(self):
        return self._field_name

    def __init__(
        self, meta: Union[str, int, float, bool], name: str, field_name: str
    ) -> None:
        super().__init__(meta)
        self._field_name = field_name
        self._name = name


class PGField(AbstractField):
    """
    Postgres field concrete class.

    (see metaclass for method docs)
    """

    @property
    def name(self) -> str:
        return f"{self.resource_name}.{self._value.column}"

    @property
    def type(self) -> str:
        return self._value.get_internal_type()

    @property
    def resource_name(self) -> str:
        return self._resource_name

    @property
    def is_primary_key(self) -> bool:
        return self.name == self._resource_primary_key

    @property
    def is_virtual(self) -> bool:
        return False

    @property
    def metadata(self) -> List[PGMetadata]:
        return [
            PGMetadata(value, name, self.name)
            for name, value in self._value.__dict__.items()
        ]

    def __init__(
        self,
        field: ModelField,
        resource_name: str,
        resource_primary_key: Optional[str] = None,
    ) -> None:
        super().__init__(field)
        self._resource_name = resource_name
        self._resource_primary_key = resource_primary_key


class PGVirtualField(PGField):
    """
    Postgres virtual field concrete class.

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


class PGRelationship(AbstractRelationship):
    """
    Postgres relationship concrete class.

    (see metaclass for method docs)
    """

    @property
    def type(self) -> str:
        return sub("Rel$", "", type(self._value).__name__)

    @property
    def field_name(self) -> str:
        return PGField(self._value.target_field, self.resource_name).name

    @property
    def related_field_name(self) -> str:
        return PGField(self._value.field, self.related_resource_name).name

    @property
    def resource_name(self) -> str:
        return self._resource_name

    @property
    def related_resource_name(self) -> str:
        return get_resource_name(self._value.related_model)

    def __init__(
        self, relationship: ForeignObjectRel, resource_name: str
    ) -> None:
        super().__init__(relationship)
        self._resource_name = resource_name


class PGResource(AbstractResource):
    """
    Postgres resource concrete class.

    (see metaclass for method docs)
    """

    @property
    def app(self) -> str:
        return self._app

    @property
    def primary_key(self) -> str:
        return PGField(self._value._meta.pk, self.name).name

    @property
    def normal_fields(self) -> List[PGField]:
        return [
            PGField(field, self.name, self.primary_key)
            for field in self._value._meta.get_fields()
            if isinstance(field, (ModelField, RelatedField))
        ]

    @property
    def virtual_fields(self) -> List[PGVirtualField]:
        fields = []

        for name in dir(self._value):
            try:
                value = getattr(self._value, name)

                if isinstance(value, property):
                    fields.append(PGVirtualField(value, name, self.name))
            except AttributeError:
                logger.info(
                    f'unable to get virtual "{name}" from {self._value}'
                )

        return fields

    @property
    def relationships(self) -> List[PGRelationship]:
        return [
            PGRelationship(field, self.name)
            for field in self._value._meta.get_fields()
            if isinstance(field, ForeignObjectRel)
        ]

    def __init__(self, resource: ModelBase, app: str) -> None:
        super().__init__(resource, "postgres")
        self._app = app
