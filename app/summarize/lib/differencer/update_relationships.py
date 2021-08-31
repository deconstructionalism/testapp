from typing import Dict

from app.database import db
from app.summarize.models import Relationship
from app.summarize.lib.extractors import (
    AbstractRelationship,
    SummarizerRelationship,
)
from app.summarize.lib.differencer.helpers import extract_top_level_data


def update_relationships(relationship_delta: Dict):
    """
    Compare marshall relationships to summarizer relationships and update
    summarizer data accordingly.
    """

    # track change counts
    counter = {"created": 0, "deleted": 0, "updated": 0}

    def is_relationship_modified(next_data: AbstractRelationship) -> bool:
        """Check if relationship has been changed."""

        prev_data = Relationship.query.filter_by(name=next_data.name).first()

        prev_flat, next_flat = (
            extract_top_level_data(SummarizerRelationship(prev_data)),
            extract_top_level_data(next_data),
        )

        if prev_flat != next_flat:
            print(prev_flat, next_flat)

        return prev_flat != next_flat

    def create_relationship(next_data: AbstractRelationship) -> None:
        """Create relationship in database."""

        flat_data = extract_top_level_data(next_data)
        relationship = Relationship(**flat_data)
        db.session.add(relationship)
        counter["created"] += 1

        print(f"  Relationship[CREATE] {next_data.name}")

    def delete_relationship(prev_data: Relationship) -> None:
        """Delete relationship in database."""

        db.session.query(Relationship).filter_by(name=prev_data.name).delete()
        counter["deleted"] += 1

        print(f"  Relationship[DELETE] {prev_data.name}")

    def update_relationship(next_data: AbstractRelationship) -> None:
        """Update relationship in database."""

        flat_data = extract_top_level_data(next_data)

        db.session.query(Relationship).filter_by(name=next_data.name).update(
            flat_data
        )
        counter["updated"] += 1

        print(f"  Relationship[UPDATE] {next_data.name}")

    print("Staging Relationship Changes...")

    # iterate through each category of relationships and stage appropriate
    # changes to database
    for next_data in relationship_delta["new"]:
        create_relationship(next_data)

    for prev_data in relationship_delta["removed"]:
        delete_relationship(prev_data)

    for next_data in relationship_delta["persisted"]:
        is_modified = is_relationship_modified(next_data)
        if is_modified:
            update_relationship(next_data)

    # commit all database changes
    db.session.commit()

    print("...Relationships Committed\n")

    print(
        "SUMMARY\n"
        + f"  created: {counter['created']}\n"
        + f"  deleted: {counter['deleted']}\n"
        + f"  updated: {counter['updated']}\n"
    )
