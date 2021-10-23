from typing import Dict, List, Tuple

from app.database import db
from app.lib.logger import logger
from app.summarize.models import Resource
from app.summarize.lib.extractors import (
    AbstractField,
    AbstractResource,
    SummarizerResource,
)
from app.summarize.lib.extractors.abstract_resource import (
    AbstractRelationship,
)
from app.summarize.lib.differencer.helpers import extract_top_level_data


def update_resources(
    resource_delta: Dict,
) -> Tuple[List[AbstractField], List[AbstractRelationship]]:
    """
    Compare marshall resources to summarizer resources and update summarizer
    data accordingly. Return all fields and relationships in marshall instance.
    """

    # collect all child fields and relationships from resources
    marshall_fields = []
    marshall_relationships = []

    # track change counts
    counter = {"created": 0, "unarchived": 0, "archived": 0, "updated": 0}

    # HELPER METHODS

    def is_resource_modified(next_data: AbstractResource) -> bool:
        """Check if resource has been changed."""

        prev_data = Resource.query.filter_by(name=next_data.name).first()

        prev_flat, next_flat = (
            extract_top_level_data(SummarizerResource(prev_data)),
            extract_top_level_data(next_data),
        )

        # do not compare database type as this will always vary between
        # marshall and summarizer resources
        del prev_flat["database_type"]
        del next_flat["database_type"]

        return prev_flat != next_flat

    def extract_children(
        next_data: AbstractResource,
    ) -> List[Tuple[AbstractField, str]]:
        """Collect child fields per resource."""

        marshall_fields.extend(next_data.fields)
        marshall_relationships.extend(next_data.relationships)

    # CRUD METHODS

    def create_resource(next_data: AbstractResource) -> None:
        """Create resource in database."""

        flat_data = extract_top_level_data(next_data)

        resource = Resource(**flat_data)
        db.session.add(resource)
        counter["created"] += 1

        logger.info(f"  Resource[CREATE] {next_data.name}")

    def archive_resource(prev_data: Resource) -> None:
        """Archive resource in database."""

        db.session.query(Resource).filter_by(name=prev_data.name).update(
            dict(is_archived=True)
        )
        counter["archived"] += 1

        logger.info(f"  Resource[ARCHIVE] {prev_data.name}")

    def unarchive_resource(next_data: AbstractResource) -> None:
        """Unarchive resource in database."""

        flat_data = extract_top_level_data(next_data)
        flat_data["is_archived"] = False

        db.session.query(Resource).filter_by(name=next_data.name).update(
            flat_data
        )
        counter["unarchived"] += 1

        logger.info(f"  Resource[UNARCHIVE] {next_data.name}")

    def update_resource(next_data: AbstractResource) -> None:
        """Update resource in database."""

        flat_data = extract_top_level_data(next_data)

        db.session.query(Resource).filter_by(name=next_data.name).update(
            flat_data
        )
        counter["updated"] += 1

        logger.info(f"  Resource[UPDATE] {next_data.name}")

    logger.info("Staging Resource Changes...")

    # iterate through each category of resources and stage appropriate changes
    # to database, while aggregating child fields
    for next_data in resource_delta["new"]:
        create_resource(next_data)
        extract_children(next_data)

    for next_data in resource_delta["restored"]:
        unarchive_resource(next_data)
        extract_children(next_data)

    for prev_data in resource_delta["removed"]:
        archive_resource(prev_data)

    for next_data in resource_delta["persisted"]:
        is_modified = is_resource_modified(next_data)
        if is_modified:
            update_resource(next_data)
        extract_children(next_data)

    # commit all database changes
    db.session.commit()

    logger.info("...Resources Committed\n")

    logger.info(
        "SUMMARY\n"
        + f"  created: {counter['created']}\n"
        + f"  archived: {counter['archived']}\n"
        + f"  unarchived: {counter['unarchived']}\n"
        + f"  updated: {counter['updated']}\n"
    )

    return (marshall_fields, marshall_relationships)
