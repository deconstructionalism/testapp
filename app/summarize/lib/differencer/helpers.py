import subprocess
from typing import Dict, List
from app.lib.logger import logger
from app.summarize.models import Field, Metadata, Resource, Relationship
from app.summarize.lib.extractors import AbstractResource


def update_marshall_repo() -> bool:
    """
    Get commit updates to marshall repo on designated branch if they exist and
    install/update packages.
    """

    cmd = f"sh ./scripts/refresh.sh"
    p = subprocess.Popen(cmd.split(" "), stdout=subprocess.PIPE)

    # log each line from stdout to logger
    for line in iter(lambda: p.stdout.readline(), b""):
        logger.info(line.decode(encoding="utf-8").strip())

    # get return code to figure out if repo had new commits fetched
    p.communicate()
    was_updated = p.returncode != 1

    return was_updated


def get_marshall_resources() -> List[AbstractResource]:
    """Get all resources from marshall app code."""

    from app.summarize.lib import MarshallModels

    models = MarshallModels()

    return (
        models.get_models("web")
        + models.get_models("dataparty")
        + models.get_models("mongo")
    )


def get_summarizer_data() -> Dict:
    """
    Get resource, field, relationship, and metadata data from summarizer
    database.
    """

    return {
        "resources": Resource.query.all(),
        "fields": Field.query.all(),
        "metadata": Metadata.query.all(),
        "relationships": Relationship.query.all(),
    }


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


def extract_top_level_data(model: object) -> Dict:
    """Get only top-level keys for a dict serializable object"""

    return {
        key: value
        for (key, value) in model.__dict__.items()
        if not isinstance(value, (list, dict))
    }


def take_commit_snapshot() -> None:
    """Get json delta for current commit compared to previous."""

    return None
