from dotenv import load_dotenv
from os import getenv

load_dotenv()


class Config:
    CSRF_ENABLED = True
    CSRF_SECRET_KEY = getenv("CSRF_SECRET_KEY")
    DEBUG = False
    DEVELOPMENT = False
    SECRET_KEY = getenv("SECRET_KEY")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    THREADS_PER_PAGE = 2


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = getenv("PRODUCTION_DATABASE_URI")


class DevelopmentConfig(Config):
    DEBUG = True
    DEVELOPMENT = True
    SQLALCHEMY_DATABASE_URI = getenv("DEVELOPMENT_DATABASE_URI")
