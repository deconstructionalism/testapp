from flask import Flask
from os import getenv
from flask_migrate import Migrate
from app.filters.controllers import filters
import click
from flask.cli import with_appcontext
from app.database import db

migrate = Migrate(None, db)


def create_app() -> Flask:
    app = Flask(__name__)
    env = getenv("ENV")
    env_config = (
        "config.ProductionConfig"
        if env == "production"
        else "config.DevelopmentConfig"
    )
    app.config.from_object(env_config)
    db.init_app(app)

    app.register_blueprint(filters)

    app.cli.add_command(init_db_command)
    migrate.init_app(app)

    return app


def init_db():
    db.drop_all()
    db.create_all()
    db.session.commit()


@click.command("init-db")
@with_appcontext
def init_db_command():
    """Clear existing data and create new tables."""

    from app.filters.models import FieldMetadataFilter
    from app.summarize.models import Resource, Field, Relationship, MetaData

    init_db()
    click.echo("Initialized the database.")
