from abc import ABCMeta, abstractmethod
from app.lib import DatabaseTypes
from dotenv import load_dotenv
from inspect import getcomments, getsourcefile, getsourcelines
from os import getenv
from os.path import relpath
from re import sub
from typing import List, Optional, Type, Union


# LOAD ENV VARIABLES

load_dotenv()

marshall_repo_base_url = getenv("MARSHALL_REPO_BASE_URL")
marshall_branch = getenv("MARSHALL_BRANCH")


# HELPER FUNCTIONS


def get_description(obj: object) -> str:
    """Get description string for an object."""

    # for builtin types, only provide type
    doc = (
        type(obj).__name__
        if type(obj).__module__ == "builtins"
        else obj.__doc__
    )
    chunks = [doc, getcomments(obj)]

    return "\n".join(filter(None, chunks))


def dict_map(obj_list: List[object]) -> List[dict]:
    """Map list of objects to their `__dict__` method outputs."""

    return [obj.__dict__ for obj in obj_list]


# ABSTRACT RESOURCE CLASSES


class AbstractMetadata(metaclass=ABCMeta):
    """Abstract metadata (singular) class for abstract `Field` class."""

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
    def value(self) -> str:
        """Get field value."""

        return ""

    @property
    @abstractmethod
    def field_name(self) -> str:
        """
        Get parent field name.
        """

        return ""

    def __init__(self, meta: Union[str, int, float, bool]) -> None:
        self._value = meta

    @property
    def __dict__(self) -> dict:
        return {
            "name": self.name,
            "field_name": self.field_name,
            "value": self.value,
            "description": self.description,
        }

    def __repr__(self) -> str:
        return f'<{type(self).__name__}: name="{self.name}">'


class AbstractField(metaclass=ABCMeta):
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
    def resource_name(self) -> str:
        """
        Get parent resource name.
        """

        return ""

    # @property
    # @abstractmethod
    # def related_resource_name(self) -> Optional[str]:
    #     """
    #     Get foreign resource name.

    #     Field is implicitly foreign key field if not `None`.
    #     """

    #     return ""

    # @property
    @abstractmethod
    def is_primary_key(self) -> bool:
        """Get whether field is a primary key field."""

        return False

    @property
    @abstractmethod
    def is_virtual(self) -> bool:
        """Get whether field is a virtual field."""

        return False

    @property
    @abstractmethod
    def metadata(self) -> List[AbstractMetadata]:
        """Get metadata."""

        return []

    def __init__(self, field: object) -> None:
        self._value = field

    @property
    def __dict__(self) -> dict:
        return {
            "name": self.name,
            "type": self.type,
            # "related_resource_name": self.related_resource_name,
            "resource_name": self.resource_name,
            "is_primary_key": self.is_primary_key,
            "is_virtual": self.is_virtual,
            "metadata": dict_map(self.metadata),
            "description": self.description,
        }

    def __repr__(self) -> str:
        return (
            f'<{type(self).__name__}: name="{self.name}" type="{self.type}">'
        )


class AbstractRelationship(metaclass=ABCMeta):
    """Abstract relationship class for abstract `Resource` class."""

    @property
    def description(self) -> str:
        """Get description string."""

        return get_description(self._value)

    @property
    def name(self) -> str:
        """Get unique name of relationship."""
        return f"{self.field_name}({self.type}){self.related_field_name}"

    @property
    @abstractmethod
    def type(self) -> str:
        """Get type of relationship."""

        return ""

    @property
    @abstractmethod
    def field_name(self) -> str:
        """Get name of foreign key field."""

        return ""

    @property
    @abstractmethod
    def resource_name(self) -> str:
        """Get name of parent resource."""

        return ""

    @property
    @abstractmethod
    def related_field_name(self) -> str:
        """Get name of reference field in related resource."""

        return ""

    @property
    @abstractmethod
    def related_resource_name(self) -> str:
        """Get name of related resource."""

        return ""

    def __init__(self, relationship: object) -> None:
        self._value = relationship

    @property
    def __dict__(self) -> dict:
        return {
            "name": self.name,
            "type": self.type,
            "field_name": self.field_name,
            "related_field_name": self.related_field_name,
            "resource_name": self.resource_name,
            "related_resource_name": self.related_resource_name,
            "description": self.description,
        }

    def __repr__(self) -> str:
        return (
            f'<{type(self).__name__}: type="{self.type}" '
            + f'to="{self.related_resource}">'
        )


class AbstractResource(metaclass=ABCMeta):
    """Abstract `Resource` class."""

    @property
    def type(self) -> str:
        """Get resource type."""

        return self._value.__bases__[0].__name__

    @property
    def name(self) -> str:
        """Get resource name."""

        return "{}.{}".format(self._value.__module__, self._value.__name__)

    @property
    def source_link(self) -> Optional[str]:
        """Get a link to module in "marshall" Github repo with line number."""

        try:
            relative_path = relpath(getsourcefile(self._value))
            if not relative_path.startswith("marshall/"):
                print(
                    f'module "{self.name}" at "{relative_path}" '
                    + 'not found in "marshall" app.'
                )
                return None

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
    def fields(self) -> List[AbstractField]:
        """Get list of all fields."""

        return [
            *self.normal_fields,
            # *self.foreign_key_fields,
            *self.virtual_fields,
        ]

    @property
    @abstractmethod
    def app(self) -> str:
        """Get resource's django app name."""

        return ""

    @property
    @abstractmethod
    def primary_key(self) -> Optional[str]:
        """Get primary key."""

        return ""

    @property
    @abstractmethod
    def normal_fields(self) -> List[AbstractField]:
        """Get list of normal fields."""

        return []

    # @property
    # @abstractmethod
    # def foreign_key_fields(self) -> List[AbstractField]:
    #     """Get list of foreign key fields."""

    #     return []

    @property
    @abstractmethod
    def virtual_fields(self) -> List[AbstractField]:
        """Get list of virtual fields."""

        return []

    @property
    @abstractmethod
    def relationships(self) -> List[AbstractRelationship]:
        """Get list of relationships."""

        return []

    def __init__(self, resource: Type, database_type: DatabaseTypes) -> None:
        self._value = resource
        self.database_type = database_type

    @property
    def __dict__(self) -> dict:
        return {
            "type": self.type,
            "name": self.name,
            "app": self.app,
            "database_type": self.database_type,
            "source_link": self.source_link,
            "description": self.description,
            "fields": dict_map(self.fields),
            "relationships": dict_map(self.relationships),
        }

    def __repr__(self) -> str:
        return (
            f'<{type(self).__name__}: type="{self.type}" name="{self.name}">'
        )
