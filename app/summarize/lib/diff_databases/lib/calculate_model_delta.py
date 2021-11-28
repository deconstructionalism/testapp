from typing import Dict, List


def calculate_model_delta(
    prev_models: List, next_models: List, archivable: bool = True
) -> Dict:
    """
    Compare previous models to next models to determine which models are new,
    restored, removed, or persisted and return names of models in each
    category. Return arrays of next models in each category except the
    "removed" category for which previous models will be returned.
    """

    if archivable:

        prev_archived_names = {m.name for m in prev_models if m.is_archived}
        prev_names = {m.name for m in prev_models if not m.is_archived}
        next_names = {m.name for m in next_models}

        new = list(next_names.difference(prev_names, prev_archived_names))
        restored = list(prev_archived_names.intersection(next_names))
        removed = list(prev_names.difference(next_names))
        persisted = list(prev_names.intersection(next_names))

        return {
            "new": [m for m in next_models if m.name in new],
            "restored": [m for m in next_models if m.name in restored],
            "removed": [m for m in prev_models if m.name in removed],
            "persisted": [m for m in next_models if m.name in persisted],
        }
    else:
        prev_names = {m.name for m in prev_models}
        next_names = {m.name for m in next_models}

        new = list(next_names.difference(prev_names))
        removed = list(prev_names.difference(next_names))
        persisted = list(prev_names.intersection(next_names))

        return {
            "new": [m for m in next_models if m.name in new],
            "removed": [m for m in prev_models if m.name in removed],
            "persisted": [m for m in next_models if m.name in persisted],
        }
