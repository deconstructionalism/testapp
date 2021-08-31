from app.lib import BaseModel, db
from sqlalchemy.dialects.postgresql import JSONB


class CommitSnapshot(BaseModel):
    __tablename__ = "commit_snapshot"

    # columns
    commit_id = db.Column(db.String(), unique=True, nullable=False)
    snapshot = db.Column(JSONB)

    # serializer config
    serialize_rules = ("-date_modified", "-id")

    def __repr__(self):
        return f'<CommitSnapshot: commit="{self.id}">'
