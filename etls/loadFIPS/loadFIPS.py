import requests
import os
import time
import pandas as pd
from pangres import upsert
import logging
import sys

from typing import Optional
from io import StringIO
from sqlalchemy import create_engine

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class FIPSCountyETL:
    def __init__(self, table_name: str = "fips_county"):
        self.table_name = table_name

        # Get environment variables from os or from aws glue context
        # TODO: We could abstract this into a python module that works either locally or in AWS
        # e.g. configuration.get("MAX_RETRIES") or configuration.get("DB_PASSWORD")
        MAX_RETRIES_KEY = "MAX_RETRIES"
        DB_SECRET_ARN = "DB_SECRET_ARN"
        DB_USER_KEY = "DB_USER"
        DB_PASSWORD_KEY = "DB_PASSWORD"
        DB_NAME_KEY = "DB_NAME"
        DB_HOST_KEY = "DB_HOST"
        DB_PORT_KEY = "DB_PORT"

        try:
            # AWS-specific flow for fetching configuration information
            from awsglue.utils import getResolvedOptions
            import boto3
            import json
            args = getResolvedOptions(sys.argv, [
                MAX_RETRIES_KEY,
                DB_SECRET_ARN,
                DB_NAME_KEY,
                DB_HOST_KEY,
                DB_PORT_KEY
            ])
            # Fetch sensitive values from secretsmanager directly
            secrets_client = boto3.client("secretsmanager", region_name="us-gov-west-1")
            db_secret = json.loads(secrets_client.get_secret_value(SecretId=args[DB_SECRET_ARN])["SecretString"])
            self.db_user = db_secret["username"] # because the key is "username" on the secret payload
            self.db_password = db_secret["password"] # because the key is "password" on the secret payload
            # Retrieve non-sensitive data from getResolvedOptions
            self.max_retries = int(os.getenv(args[MAX_RETRIES_KEY], "3"))
            self.db_name = args[DB_NAME_KEY]
            self.db_host = args[DB_HOST_KEY]
            self.db_port = args[DB_PORT_KEY]

        except ImportError:
            from dotenv import load_dotenv
            load_dotenv()
            # Fallback to fetching information from a local .env using dotenv
            self.max_retries = int(os.getenv(MAX_RETRIES_KEY, "3"))
            self.db_user = os.getenv(DB_USER_KEY)
            self.db_password = os.getenv(DB_PASSWORD_KEY)
            self.db_name = os.getenv(DB_NAME_KEY)
            self.db_host = os.getenv(DB_HOST_KEY)
            self.db_port = os.getenv(DB_PORT_KEY)

    def handle_request(self, url: str) -> Optional[requests.Response]:
        for attempt in range(self.max_retries):
            try:
                # important to note that we get responses back as .txt and not .json
                response = requests.get(url, timeout=30)
                response.raise_for_status()

                return response
            except requests.HTTPError as e:
                if e.response.status_code == 404:
                    logger.error(f"404 Error for URL: {url}")
            except requests.Timeout as e:
                logger.error(
                    f"Timeout error has occurred after waiting 30 seconds.")
            except requests.RequestException as e:
                if attempt == self.max_retries - 1:
                    logger.error(f"Failed to fetch after 3 attempts: {e}")
                    return None
                else:
                    sleep = 2 ** attempt
                    logger.warning(
                        f"Attempt {attempt} failed so retrying in {sleep} seconds.")

                    time.sleep(sleep)
            except Exception as e:
                logger.error(
                    f"Something went wrong with handling a request: {e}")
                raise
        return None

    def validate_data(self, df: pd.DataFrame) -> None:
        required_columns = ["STATEFP", "COUNTYFP", "COUNTYNAME"]
        STATEFP_regex = r'^\d{2}$'
        COUNTYFP_regex = r'^\d{3}$'

        for column in required_columns:
            if column not in df.columns:
                raise ValueError(f"Missing required column: {column}")

        if df.empty:
            raise ValueError("DataFrame is empty!")
        if not df["STATEFP"].str.match(STATEFP_regex).all():
            raise ValueError("STATEFP should be a 2 digit code")
        if not df["COUNTYFP"].str.match(COUNTYFP_regex).all():
            raise ValueError("COUNTYFP should be a 3 digit code")

    def extract(self) -> str:
        url = "https://www2.census.gov/geo/docs/reference/codes2020/national_county2020.txt"

        response = self.handle_request(url)
        raw_data = response.text

        logger.info("Phase 1 - Extraction has finished")
        return raw_data

    def transform(self) -> pd.DataFrame:
        raw_data = self.extract()

        try:
            df = pd.read_csv(StringIO(raw_data), delimiter="|", dtype=str)

            self.validate_data(df)

            df = df[["STATEFP", "COUNTYFP", "COUNTYNAME"]].copy()

            df["id"] = df["STATEFP"] + df["COUNTYFP"]
            df["name"] = df["COUNTYNAME"]
            df["fips_state_id"] = df["STATEFP"]

            df = df[["id", "name", "fips_state_id"]].drop_duplicates()
            df = df.set_index("id")

        except Exception as e:
            logger.error(
                f"Something went wrong transforming the raw data: {e}")
            raise

        logger.info("Phase 2 - Transformation has finished")
        # df.to_csv("output.csv", index=False)

        return df

    def load(self):
        transformed_data = self.transform()

        connection_string = (
            f"postgresql://{self.db_user}:{self.db_password}@"
            f"{self.db_host}:{self.db_port}/{self.db_name}"
        )

        engine = create_engine(connection_string)

        try:
            with engine.begin() as con:
                upsert(
                    con=con,
                    df=transformed_data,
                    table_name=self.table_name,
                    if_row_exists="update",
                    schema = "ndh"
                )

            logger.info("Phase 3 - Loading has finished")
            logger.info(
                f"  Successfully loaded {len(transformed_data)} records to {self.table_name} table!")

        except Exception as e:
            logger.error(
                f"Something went wrong loading the transformed data: {e}")
            raise
        finally:
            engine.dispose()

    def run_pipeline(self):
        try:
            logger.info("Starting FIPS County ETL pipeline!")
            self.load()
            logger.info("Pipeline completed successfully!")

        except Exception as e:
            logger.error(f"Something went wrong with the pipeline: {e}")
            raise


def main():
    pipeline = FIPSCountyETL()
    pipeline.run_pipeline()


if __name__ == "__main__":
    main()
