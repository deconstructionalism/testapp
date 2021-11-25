from flask import current_app
from typing import Callable
from app.lib.logger import logger
from app.summarize.lib.differencer.update_fields import update_fields
from app.summarize.lib.differencer.update_metadata import update_metadata
from app.summarize.lib.differencer.update_relationships import (
    update_relationships,
)
from app.summarize.lib.differencer.update_resources import update_resources
from app.summarize.lib.differencer.helpers import (
    calculate_model_delta,
    get_marshall_resources,
    get_summarizer_data,
    take_commit_snapshot,
    update_marshall_repo,
)


def update_database(on_complete: Callable, force: bool = False) -> None:
    """
    Compare current marshall repo models to summarizer database data
    and update database to reflect marshall models.
    """

    from app import create_app

    app = None

    # check if there is already an app context to use
    if current_app:
        app = current_app
    # if not, create app context to access database
    else:
        app = create_app()
        app.app_context().push()

    # fetch latest changes to marshall
    was_updated = update_marshall_repo()

    # take snapshot delta of commits from current version which will now
    # be archived
    take_commit_snapshot()

    # do not sync data if marshall was not updated, unless `force === True`
    if not was_updated and not force:
        logger.info("REFRESH COMPLETE")

        on_complete()
        return

    # extract data from marshall and from summarizer DB
    marshall_resources = get_marshall_resources()
    summarizer_data = get_summarizer_data()

    # update marshall resource data in summarizer
    resource_delta = calculate_model_delta(
        summarizer_data["resources"], marshall_resources
    )

    marshall_fields, marshall_relationships = update_resources(resource_delta)

    # update marshall field data in summarizer
    field_delta = calculate_model_delta(
        summarizer_data["fields"], marshall_fields
    )

    marshall_metadata = update_fields(field_delta)

    # update marshall metadata in summarizer
    metadata_delta = calculate_model_delta(
        summarizer_data["metadata"], marshall_metadata, False
    )

    update_metadata(metadata_delta)

    # update marshall relationships in summarizer
    relationship_delta = calculate_model_delta(
        summarizer_data["relationships"], marshall_relationships, False
    )

    update_relationships(relationship_delta)

    logger.info("REFRESH COMPLETE")

    on_complete()
