from os import getenv


class Config:
    CSRF_ENABLED = True
    CSRF_SECRET_KEY = getenv("CSRF_SECRET_KEY")
    DEBUG = False
    DEVELOPMENT = True
    SECRET_KEY = getenv("SECRET_KEY")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    THREADS_PER_PAGE = 2


user = getenv("POSTGRES_USER")
password = getenv("POSTGRES_PASSWORD")


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{user}:{password}@localhost/summarizer_production"
    )


class DevelopmentConfig(Config):
    DEBUG = True
    DEVELOPMENT = True
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{user}:{password}@localhost/summarizer_development"
    )
