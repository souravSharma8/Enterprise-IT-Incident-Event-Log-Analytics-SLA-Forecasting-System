import os
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

def get_engine() -> Engine:
    """
    Creates and returns a SQLAlchemy Engine for MySQL using PyMySQL.
    Reads connection info from environment variables.
    If 'TESTING' is set to 'True', returns an in-memory SQLite engine.
    """
    if os.getenv("TESTING", "False").lower() == "true":
        # For simple pytest runs without a DB
        return create_engine("sqlite:///test.db", echo=False)

    host = os.getenv("DB_HOST", "127.0.0.1")
    port = os.getenv("DB_PORT", "3306")
    user = os.getenv("DB_USER", "root")
    password = os.getenv("DB_PASSWORD", "password")
    db_name = os.getenv("DB_NAME", "incident_intelligence")

    connection_string = f"mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}"
    return create_engine(connection_string, pool_pre_ping=True)
