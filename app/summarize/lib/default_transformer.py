from typing import Any, Callable, Mapping


Transformer = Callable[[object, str], Any]
TypeGetter = Callable[[object], str]


class DefaultTransformer:
    """
    Repository of type-specific object transformers that can be called directly
    on objects.

    `get_type` specifies a callback to find the type of any object
    input into this class.

    Type-specific transformers can be added to instance using the `register`
    instance method.

    On transform, class will default to a default transformer if type is not
    found in 'transformers' property.
    """

    def __init__(self, get_type: TypeGetter, default: Transformer,) -> None:
        self.__default = default
        self.__get_type = get_type
        self.__transformers = {}

    @property
    def transformers(self) -> Mapping[str, Transformer]:
        """Get registered type transformers."""

        return self.__transformers

    def register(self, item_type: str, extractor: Transformer) -> None:
        """Register a type transformer."""

        self.__transformers[item_type] = extractor

    def __call__(self, item: Any) -> Any:
        """Transform an item."""

        item_type = self.__get_type(item)

        # find transformer for item type or use default transfomer
        extractor = (
            self.__transformers[item_type]
            if item_type in self.__transformers
            else self.__default
        )

        return extractor(item, item_type)
