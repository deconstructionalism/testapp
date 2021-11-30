from app.database import db
from app.lib.logger import logger
from app.summarize.lib.extractors.summarizer import SummarizerResource
from app.summarize.models import CommitSnapshot, Resource
from jsonpatch import JsonPatch
import subprocess


# HELPER FUNCTIONS


def get_marshall_commit_id() -> str:
    """Get commit id of marshall repo."""

    cmd = "git -C ./marshall rev-parse HEAD"
    output = subprocess.check_output(cmd.split(" "))

    return output.decode("ascii").strip()


def take_commit_snapshot() -> None:
    """
    Get and save json diff for current commit compared to previous as a
    `CommitSnapshot`.
    """

    logger.info("Taking Commit Snapshot of Summarizer Resources...")

    current_commit_id = get_marshall_commit_id()

    # check if commit already has snapshot, and abort if so
    commit_exists_query = CommitSnapshot.query.filter(
        CommitSnapshot.commit_id == current_commit_id
    )
    if db.session.query(commit_exists_query.exists()):
        logger.warn(f"  commit {current_commit_id} already has snapshot")
        logger.info("...Commit Snapshot Aborted")
        return

    logger.info(f"  commit: {current_commit_id}")

    # get current resource data
    resources = [
        SummarizerResource(resource).__dict__
        for resource in Resource.query.all()
    ]

    # calculate previous resources state based on commit snapshots
    previous_diffs = [
        diff
        for snapshot in CommitSnapshot.query.all()
        for diff in snapshot.diff
    ]
    previous_resources = JsonPatch(previous_diffs).apply({})

    # calculate diff to get from `previous_resources` to `resources`
    next_diff = JsonPatch.from_diff(previous_resources, resources)

    # create new `CommitSnapshot`
    commit_snapshot = CommitSnapshot(
        commit_id=current_commit_id, diff=next_diff.patch
    )

    db.session.add(commit_snapshot)
    db.session.commit()

    logger.info(f"...Commit Snapshot Created")

    return
