from typing import Dict

from app.database import db
from app.summarize.models import Metadata
from app.summarize.lib.extractors import (
    AbstractMetadata,
    SummarizerMetadata,
)
from app.summarize.lib.differencer.helpers import extract_top_level_data


def update_metadata(metadata_delta: Dict) -> None:
    """
    Compare marshall metadata to summarizer metadata and update summarizer
    data accordingly.
    """

    # track change counts
    counter = {"created": 0, "deleted": 0, "updated": 0}

    def is_metadata_modified(next_data: AbstractMetadata) -> bool:
        """Check if metadata has been changed."""

        prev_data = Metadata.query.filter_by(name=next_data.name).first()

        prev_flat, next_flat = (
            extract_top_level_data(SummarizerMetadata(prev_data)),
            extract_top_level_data(next_data),
        )

        return prev_flat != next_flat

    def create_metadata(next_data: AbstractMetadata) -> None:
        """Create metadata in database."""

        flat_data = extract_top_level_data(next_data)
        metadata = Metadata(**flat_data)
        db.session.add(metadata)
        counter["created"] += 1

        print(f"  Metadata[CREATE] {next_data.name}")

    def delete_metadata(prev_data: Metadata) -> None:
        """Delete metadata from database."""

        db.session.query(Metadata).filter_by(name=prev_data.name).delete()
        counter["deleted"] += 1

        print(f"  Metadata[DELETE] {prev_data.name}")

    def update_metadata(next_data: AbstractMetadata) -> None:
        """Update metadata in database."""

        flat_data = extract_top_level_data(next_data)

        db.session.query(Metadata).filter_by(name=next_data.name).update(
            flat_data
        )
        counter["updated"] += 1

        print(f"  Metadata[UPDATE] {next_data.name}")

    print("Staging Metadata Changes...")

    # iterate through each category of metadata and stage appropriate changes
    # to database
    for next_data in metadata_delta["new"]:
        create_metadata(next_data)

    for prev_data in metadata_delta["removed"]:
        delete_metadata(prev_data)

    for next_data in metadata_delta["persisted"]:
        is_modified = is_metadata_modified(next_data)
        if is_modified:
            update_metadata(next_data)

    # commit all database changes
    db.session.commit()

    print("...Metadata Committed\n")

    print(
        "SUMMARY\n"
        + f"  created: {counter['created']}\n"
        + f"  deleted: {counter['deleted']}\n"
        + f"  updated: {counter['updated']}\n"
    )
