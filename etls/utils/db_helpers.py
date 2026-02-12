import os
from sqlalchemy import create_engine


def createEngine(env_var_prefix="NPD"):
    # Get database details and create engine
    username = os.getenv(f"{env_var_prefix}_DB_USER")
    password = os.getenv(f"{env_var_prefix}_DB_PASSWORD")
    instance = os.getenv(f"{env_var_prefix}_DB_HOST")
    db = os.getenv(f"{env_var_prefix}_DB_NAME")
    port = os.getenv(f"{env_var_prefix}_DB_PORT")
    engine = create_engine(
        f"postgresql+psycopg2://{username}:{password}@{instance}:{port}/{db}"
    )
    return engine
