from flask_sqlalchemy import SQLAlchemy

# SQLALchemy instance is defined in isolation here to allow import into
# various module contexts without throwing app context errors
db = SQLAlchemy()
