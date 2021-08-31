import subprocess
from typing import Dict, List
from dotenv import load_dotenv
from os import getenv

from app.summarize.models import Field, Metadata, Resource, Relationship
from app.summarize.lib.extractors import AbstractResource

load_dotenv()


def update_marshall_repo() -> None:
    """
    Get commit updates to marshall repo on designated branch if they exist.
    """

    cmd = f"git -C marshall/ pull --force origin {getenv('MARSHALL_BRANCH')}"
    p = subprocess.Popen(cmd.split(" "), stdout=subprocess.PIPE)

    out = p.communicate()

    if "Already up to date" in str(out):
        print(
            f"marshall branch \"{getenv('MARSHALL_BRANCH')}\" already up "
            + "to date"
        )


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

