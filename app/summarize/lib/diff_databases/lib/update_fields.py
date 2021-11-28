from app.database import db
from app.lib.logger import logger
from app.summarize.models import Field
from app.summarize.lib.extractors import (
    AbstractField,
    AbstractMetadata,
    SummarizerField,
)
from app.summarize.lib.diff_databases.lib.helpers import (
    extract_top_level_data,
)
from typing import Dict, List, Tuple


def update_fields(field_delta: Dict) -> List[AbstractMetadata]:

    # collect all child metadata from fields
    marshall_metadata = []

    # track change counts
    counter = {"created": 0, "unarchived": 0, "archived": 0, "updated": 0}

    # HELPER METHODS

    def is_field_modified(next_data: AbstractField) -> bool:
        """Check if field has been changed."""

        prev_data = Field.query.filter_by(name=next_data.name).first()

        prev_flat, next_flat = (
            extract_top_level_data(SummarizerField(prev_data)),
            extract_top_level_data(next_data),
        )

        return prev_flat != next_flat

    def extract_meta(
        next_data: AbstractField,
    ) -> List[Tuple[AbstractMetadata, str]]:
        """Collect child metadata per resource."""

        marshall_metadata.extend(next_data.metadata)

    # CRUD METHODS

    def create_field(next_data: AbstractField) -> None:
        """Create field in database."""

        flat_data = extract_top_level_data(next_data)
        field = Field(**flat_data)
        db.session.add(field)
        counter["created"] += 1

        logger.info(f"  Field[CREATE] {next_data.name}")

    def archive_field(prev_data: Field) -> None:
        """Archive field in database."""

        db.session.query(Field).filter_by(name=prev_data.name).update(
            dict(is_archived=True)
        )
        counter["archived"] += 1

        logger.info(f"  Field[ARCHIVE] {prev_data.name}")

    def unarchive_field(next_data: AbstractField) -> None:
        """Unarchive field in database."""

        flat_data = extract_top_level_data(next_data)
        flat_data["is_archived"] = False

        db.session.query(Field).filter_by(name=next_data.name).update(
            flat_data
        )
        counter["unarchived"] += 1

        logger.info(f"  Field[UNARCHIVE] {next_data.name}")

    def update_field(next_data: AbstractField) -> None:
        """Update field in database."""

        flat_data = extract_top_level_data(next_data)

        db.session.query(Field).filter_by(name=next_data.name).update(
            flat_data
        )
        counter["updated"] += 1

        logger.info(f"  Field[UPDATE] {next_data.name}")

    logger.info("Staging Field Changes...")

    # iterate through each category of fields and stage appropriate changes
    # to database, while aggregating child metadata
    for next_data in field_delta["new"]:
        create_field(next_data)
        extract_meta(next_data)

    for next_data in field_delta["restored"]:
        unarchive_field(next_data)
        extract_meta(next_data)

    for prev_data in field_delta["removed"]:
        archive_field(prev_data)

    for next_data in field_delta["persisted"]:
        is_modified = is_field_modified(next_data)
        if is_modified:
            update_field(next_data)
        extract_meta(next_data)

    # commit all database changes
    db.session.commit()

    logger.info("...Fields Committed\n")

    logger.info(
        "SUMMARY\n"
        + f"  created: {counter['created']}\n"
        + f"  archived: {counter['archived']}\n"
        + f"  unarchived: {counter['unarchived']}\n"
        + f"  updated: {counter['updated']}\n"
    )

    return marshall_metadata
