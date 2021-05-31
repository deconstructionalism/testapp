from abc import ABCMeta, abstractmethod
from dotenv import load_dotenv
from inspect import (
    getcomments,
    getsourcefile,
    getsourcelines,
)
from os import getenv
from os.path import relpath
from re import sub
from typing import Any, List, Type, Union


# LOAD ENV VARIABLES

load_dotenv()

marshall_repo_base_url = getenv("MARSHALL_REPO_BASE_URL")
marshall_branch = getenv("MARSHALL_BRANCH")


def get_description(obj: object) -> str:
    """Get description string for an object."""

    chunks = [obj.__doc__, getcomments(obj)]
    return "\n".join(filter(None, chunks))


def dict_map(obj_list: List[object]) -> List[dict]:
    """Map list of objects to their `__dict__` method outputs."""

    return [obj.__dict__() for obj in obj_list]


# ABSTRACT RESOURCE CLASSES


class Meta(metaclass=ABCMeta):
    """Abstract metadata (singular) class for abstract `Field` class."""

    @property
    def description(self) -> str:
        """Get description string."""

        return get_description(self._value)

    def __init__(self, meta: Union[str, int, float, bool], name: str) -> None:
        self._value = meta
        self.name = name
        self.value = meta

    def __dict__(self) -> dict:
        return {
            "name": self.name,
            "value": self.value,
            "description": self.description,
        }


class Field(metaclass=ABCMeta):
    """Abstract field class for abstract `Resource` class."""

    @property
    def description(self) -> str:
        """Get description string."""

        return get_description(self._value)

    @property
    @abstractmethod
    def name(self) -> str:
        """Get field name."""

        return ""

    @property
    @abstractmethod
    def type(self) -> str:
        """Get field type."""

        return ""

    @property
    @abstractmethod
    def metadata(self) -> List[Meta]:
        """Get metadata."""

        return []

    def __init__(self, field: object) -> None:
        self._value = field

    def __dict__(self) -> dict:
        return {
            "name": self.name,
            "type": self.type,
            "metadata": dict_map(self.metadata),
            "description": self.description,
        }


class ForeignKeyField(Field, metaclass=ABCMeta):
    """Abstract foreign key field class for abstract `Resource` class."""

    @property
    @abstractmethod
    def related_resource(self) -> str:
        """Get name of related resource."""

        return ""

    @property
    @abstractmethod
    def related_field(self) -> str:
        """Get name of reference field in related resource."""

        return ""

    def __dict__(self) -> dict:
        field_dict = super().__dict__()

        return dict(
            field_dict,
            **{
                "related_resource": self.related_resource,
                "related_field": self.related_field,
            },
        )


class Relationship(metaclass=ABCMeta):
    """Abstract relationship class for abstract `Resource` class."""

    @property
    def description(self) -> str:
        """Get description string."""

        return get_description(self._value)

    @property
    @abstractmethod
    def type(self) -> str:
        """Get type of relationship."""

        return ""

    @property
    @abstractmethod
    def field(self) -> str:
        """Get name of foreign key field."""

        return ""

    @property
    @abstractmethod
    def related_resource(self) -> str:
        """Get name of related resource."""

        return ""

    @property
    @abstractmethod
    def related_field(self) -> str:
        """Get name of reference field in related resource."""

        return ""

    def __init__(self, relationship: object) -> None:
        self._value = relationship

    def __dict__(self) -> dict:
        return {
            "type": self.type,
            "field": self.field,
            "related_resource": self.related_resource,
            "related_field": self.related_field,
            "description": self.description,
        }


class Resource(metaclass=ABCMeta):
    """Abstract `Resource` class."""

    @property
    def type(self) -> str:
        """Get resource type."""

        return self._value.__bases__[0].__name__

    @property
    def name(self) -> str:
        """Get resource name."""

        return "{}.{}".format(
            self._value.__module__, self._value.__name__
        )

    @property
    def source_link(self) -> str:
        """Get a link to module in "marshall" Github repo with line number."""

        try:
            relative_path = relpath(getsourcefile(self._value))
            if not relative_path.startswith("marshall/"):
                return (
                    f'module "{self.name}" at "{relative_path}" '
                    + 'not found in "marshall" app.'
                )

            module_route = sub("^marshall/", "", relative_path)
            start_line = getsourcelines(self._value)[1]

            return "{}/tree/{}/{}#L{}".format(
                marshall_repo_base_url,
                marshall_branch,
                module_route,
                start_line,
            )
        except (OSError):
            print("unable to get source link for {}".format(self._value))

    @property
    def description(self) -> str:
        """Get description string."""

        return get_description(self._value)

    @property
    @abstractmethod
    def primary_key(self) -> str:
        """Get primary key."""

        return ""

    @property
    @abstractmethod
    def fields(self) -> List[Field]:
        """Get list of fields."""

        return []

    @property
    @abstractmethod
    def foreign_key_fields(self) -> List[ForeignKeyField]:
        """Get list of foreign key fields."""

        return []

    @property
    @abstractmethod
    def virtual_fields(self) -> List[Field]:
        """Get list of virtual fields."""

        return []

    @property
    @abstractmethod
    def relationships(self) -> List[Relationship]:
        """Get list of relationships."""

        return []

    def __init__(self, resource: Type, database_type: str) -> None:
        self._value = resource
        self.database_type = database_type

    def __dict__(self) -> dict:
        return {
            "type": self.type,
            "name": self.name,
            "database_type": self.database_type,
            "source_link": self.source_link,
            "description": self.description,
            "primary_key": self.primary_key,
            "fields": dict_map(self.fields),
            "foreign_key_fields": dict_map(self.foreign_key_fields),
            "virtual_fields": dict_map(self.virtual_fields),
            "relationships": dict_map(self.relationships),
        }
