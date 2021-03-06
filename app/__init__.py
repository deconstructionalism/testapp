from app.comments import comment_blueprint
from app.database import db
from app.filters import filter_blueprint
from app.lib.logger import logger
from app.routes import root_blueprint
from app.summarize import summarize_blueprint
from app.summarize.lib.diff_databases import diff_databases
from dotenv import load_dotenv
from flask import Flask
from flask.cli import with_appcontext
from os import getenv
from sqlalchemy import create_engine
import click

# load env variables
load_dotenv()
env = getenv("FLASK_ENV") or "production"
user = getenv("POSTGRES_USER")
password = getenv("POSTGRES_PASSWORD")


def create_app() -> Flask:
    """Create a flask app instance."""

    app = Flask(__name__)
    app.url_map.strict_slashes = False

    # load app configuration based on `ENV` environmental var
    env_config = (
        "config.ProductionConfig"
        if env == "production"
        else "config.DevelopmentConfig"
    )
    app.config.from_object(env_config)

    # set up database
    db.init_app(app)

    # register all blueprints
    app.register_blueprint(comment_blueprint)
    app.register_blueprint(filter_blueprint)
    app.register_blueprint(root_blueprint)
    app.register_blueprint(summarize_blueprint)

    # add `flask init-db` shell command
    app.cli.add_command(init_db_command)

    return app


@click.command("init-db")
@with_appcontext
def init_db_command():
    """
    Clear existing data and create new tables. For use from command line via
    `flask init-db` command.
    """

    # all tables to be initalized must be loaded here in order for them
    # to be seen by `create_all` below
    from app.comments.models import FieldComment, ResourceComment, Comment
    from app.filters.models import FieldFilter, MetadataFilter, ResourceFilter
    from app.summarize.models import (
        CommitSnapshot,
        Field,
        Metadata,
        Relationship,
        Resource,
    )

    # create the database instance based on the `env`
    engine = create_engine(
        f"postgresql://{user}:{password}@localhost/postgres"
    )
    db_name = (
        "summarizer_production"
        if env == "production"
        else "summarizer_development"
    )

    with engine.connect() as conn:
        conn.execute("commit")
        conn.execute(f"CREATE DATABASE {db_name}")

    # drop all database tables and create new ones based on above models
    db.drop_all()
    db.create_all()
    db.session.commit()

    logger.info(f"Initialized the {env} database.")

    diff_databases(lambda: None, True)
