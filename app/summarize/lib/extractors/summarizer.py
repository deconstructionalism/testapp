from app.summarize.lib.extractors import (
    AbstractField,
    AbstractMetadata,
    AbstractRelationship,
    AbstractResource,
)
from typing import List
from app.summarize.models import Field, Metadata, Relationship, Resource


# MAIN CLASSES


class SummarizerMetadata(AbstractMetadata):
    """Summarizer field metadata (singular) concrete class."""

    @property
    def name(self) -> str:
        return self._value.name

    @property
    def value(self) -> str:
        return self._value.value

    @property
    def field_name(self) -> str:
        return self._value.field_name

    @property
    def description(self) -> str:
        return self._value.description

    def __init__(self, meta: Metadata) -> None:
        super().__init__(meta)


class SummarizerField(AbstractField):
    """
    Summarizer field concrete class.

    (see metaclass for method docs)
    """

    @property
    def description(self) -> str:
        return self._value.description

    @property
    def name(self) -> str:
        return self._value.name

    @property
    def type(self) -> str:
        return self._value.type

    @property
    def resource_name(self) -> None:
        return self._value.resource_name

    # @property
    # def related_resource_name(self) -> None:
    #     return self._value.related_resource_name

    @property
    def is_primary_key(self) -> bool:
        return self._value.is_primary_key

    @property
    def is_virtual(self) -> bool:
        return self._value.is_virtual

    @property
    def metadata(self) -> List[SummarizerMetadata]:
        return [SummarizerMetadata(meta) for meta in self._value.meta_data]

    def __init__(self, field: Field) -> None:
        super().__init__(field)


class SummarizerRelationship(AbstractRelationship):
    """
    Summarizer relationship concrete class.

    (see metaclass for method docs)
    """

    @property
    def description(self) -> str:
        return self._value.description

    @property
    def type(self) -> str:
        return self._value.type

    @property
    def field_name(self) -> str:
        return self._value.field_name

    @property
    def related_field_name(self) -> str:
        return self._value.related_field_name

    @property
    def resource_name(self) -> str:
        return self._value.resource_name

    @property
    def related_resource_name(self) -> str:
        return self._value.related_resource_name

    def __init__(self, relationship: Relationship) -> None:
        super().__init__(relationship)


class SummarizerResource(AbstractResource):
    """
    Summarizer resource concrete class.

    (see metaclass for method docs)
    """

    @property
    def type(self) -> str:
        return self._value.type

    @property
    def name(self) -> str:
        return self._value.name

    @property
    def app(self) -> str:
        return self._value.app

    @property
    def source_link(self) -> str:
        return self._value.source_link

    @property
    def description(self) -> str:
        return self._value.description

    @property
    def virtual_fields(self) -> List:
        return []

    @property
    def normal_fields(self) -> List:
        return []

    @property
    def fields(self) -> List[SummarizerField]:
        return [
            SummarizerField(field)
            for field in self._value.fields
        ]

    # @property
    # def foreign_key_fields(self) -> List[SummarizerField]:
    #     return []

    @property
    def primary_key(self) -> str:
        return self._value.primary_key

    @property
    def relationships(self) -> List[SummarizerRelationship]:
        return [
            SummarizerRelationship(relationship)
            for relationship in self._value.relationships
        ]

    def __init__(self, resource: Resource) -> None:
        super().__init__(resource, "summarizer")
