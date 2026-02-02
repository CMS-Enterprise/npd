import os
from dotenv import load_dotenv
from sqlalchemy import create_engine


def createEngine():
    # Get database details and create engine
    load_dotenv()
    username = os.getenv("SOURCE_DB_USER")
    password = os.getenv("SOURCE_DB_PASSWORD")
    instance = os.getenv("SOURCE_DB_HOST")
    db = os.getenv("SOURCE_DB_NAME")
    port = os.getenv("SOURCE_DB_PORT")
    engine = create_engine(
        f"postgresql+psycopg2://{username}:{password}@{instance}:{port}/{db}"
    )
    return engine
