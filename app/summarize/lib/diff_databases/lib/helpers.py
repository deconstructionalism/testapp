from typing import Dict


def extract_top_level_data(model: object) -> Dict:
    """Get only top-level keys for a dict serializable object"""

    return {
        key: value
        for (key, value) in model.__dict__.items()
        if not isinstance(value, (list, dict))
    }
