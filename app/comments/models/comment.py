from app.lib import BaseModel, db


class Comment(BaseModel):
    __tablename__ = "comment"

    # columns
    body = db.Column(db.Text(), nullable=False)
    email = db.Column(db.String(), default="field", nullable=False)

    def __repr__(self):
        return f"<Comment email={self.email}>"
