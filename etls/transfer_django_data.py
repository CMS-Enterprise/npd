import pandas as pd
from utils.db_helpers import createEngine
from dotenv import load_dotenv

# Load the environment variables from the .env file
load_dotenv()

npd_engine = createEngine("NPDNEW")
halloween_engine = createEngine("HALLOWEEN")

for table in [
    "auth_group",
    "auth_group_permissions",
    "auth_permission",
    "auth_user",
    "auth_user_groups",
    "auth_user_user_permissions",
    "django_admin_log",
    "django_content_type",
    "django_session",
    "flags_flagstate",
]:
    df = pd.read_sql(f"select * from {table}", con=halloween_engine)
    try:
        df.to_sql(
            table, con=npd_engine, index=False, if_exists="append", schema="public"
        )
    except:
        print(f"skipping {table}")
