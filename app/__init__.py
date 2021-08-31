from app.database import db
from app.filters.controllers import filters
from app.lib.logger import logger
from app.summarize.controllers import summarize
from flask import Flask
from flask.cli import with_appcontext
from os import getenv
import click


def create_app() -> Flask:
    """Create a flask app instance."""

    app = Flask(__name__)
    app.url_map.strict_slashes = False

    # load app configuration based on `ENV` environmental var
    env = getenv("ENV")
    env_config = (
        "config.ProductionConfig"
        if env == "production"
        else "config.DevelopmentConfig"
    )
    app.config.from_object(env_config)

    # set up database
    db.init_app(app)

    # register all blueprints
    app.register_blueprint(filters)
    app.register_blueprint(summarize)

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
    # to be seen by `create_all` belwo
    from app.filters.models import MetadataFilter, FieldFilter, ResourceFilter
    from app.summarize.models import Resource, Field, Relationship, Metadata

    # drop all database tables and create new ones based on above models
    db.drop_all()
    db.create_all()
    db.session.commit()

    logger.info("Initialized the database.")
