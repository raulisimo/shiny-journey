import logging
import os
from typing import Optional

import pymysql
from dotenv import load_dotenv
from google.cloud import secretmanager
from google.cloud.sql.connector import Connector, IPTypes
from sqlalchemy import create_engine


class BaseSettings:
    """
    Base class for application settings
    """

    APP_TITLE: str
    OMDB_API_KEY: str
    DEBUG: bool

    def __init__(self):
        """Initialize base settings"""
        self.APP_TITLE = self.get_config_value("APP_TITLE")
        self.OMDB_API_KEY = self.get_config_value("OMDB_API_KEY")
        self.DEBUG = self.get_debug_mode()

    def get_config_value(self, key: str) -> str:
        """Abstract method to fetch configuration values"""
        raise NotImplementedError("Subclasses must implement `get_config_value`")

    def get_debug_mode(self) -> bool:
        """Default debug mode is False."""
        return False

    def get_db_connection(self):
        """Abstract method to get database connection"""
        raise NotImplementedError("Subclasses must implement `get_db_connection`")


class DevSettings(BaseSettings):
    """
    Development settings loaded from .env
    """

    DATABASE_URL: str

    def __init__(self):
        """Initialize development settings"""
        load_dotenv()  # Load .env for development
        self.DATABASE_URL = self.get_config_value("DATABASE_URL")
        super().__init__()

    def get_config_value(self, key: str) -> str:
        """Get the value from environment variables."""
        value = os.getenv(key)
        if not value:
            raise ValueError(f"Missing required configuration: {key}")
        return value

    def get_debug_mode(self) -> bool:
        """Enable debug mode in development"""
        return os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")

    def get_db_connection(self):
        """Create a connection to the local SQLite database"""
        if not self.DATABASE_URL:
            raise ValueError("DATABASE_URL is not configured.")
        return create_engine(self.DATABASE_URL)


class ProdSettings(BaseSettings):
    """
    Production settings loaded from Google Secret Manager
    """

    def __init__(self, gcp_project_id: Optional[str] = None):
        """Initialize production settings using GCP Secret Manager"""
        self.gcp_project_id = gcp_project_id or os.getenv("GCP_PROJECT_ID")
        if not self.gcp_project_id:
            raise ValueError("Missing required GCP_PROJECT_ID for production")
        self.secret_manager_client = secretmanager.SecretManagerServiceClient()
        super().__init__()

    def get_config_value(self, key: str) -> str:
        """Fetch configuration from Google Secret Manager"""
        secret_name = f"projects/{self.gcp_project_id}/secrets/{key}/versions/latest"
        try:
            response = self.secret_manager_client.access_secret_version(request={"name": secret_name})
            return response.payload.data.decode("UTF-8")
        except Exception as e:
            logging.error(f"Error fetching secret '{key}' from Secret Manager: {e}")
            raise ValueError(f"Error fetching secret '{key}' from Secret Manager") from e

    def get_db_connection(self):
        """Create a connection to the Cloud SQL database"""
        connection_name = os.getenv("CLOUD_SQL_CONNECTION_NAME")
        if not connection_name:
            raise ValueError("CLOUD_SQL_CONNECTION_NAME is not configured.")

        db_user = os.getenv("DB_USER", "root")
        db_name = os.getenv("DB_NAME", "brite-movies")
        db_password = self.get_config_value("DB_PASSWORD")

        ip_type = IPTypes.PRIVATE if os.getenv("PRIVATE_IP", "").lower() in ("true", "1", "yes") else IPTypes.PUBLIC

        connector = Connector(ip_type)

        def getconn() -> pymysql.connections.Connection:
            return connector.connect(
                connection_name,
                "pymysql",
                user=db_user,
                password=db_password,
                db=db_name,
            )

        return create_engine("mysql+pymysql://", creator=getconn)


class SettingsFactory:
    """
    Factory to instantiate the appropriate settings class based on environment
    """

    @staticmethod
    def get_settings() -> BaseSettings:
        """Return the settings instance based on the current environment"""
        environment = os.getenv("ENV", "DEV").upper()
        if environment == "DEV":
            return DevSettings()
        elif environment == "PRO":
            return ProdSettings()
        else:
            raise ValueError(f"Unsupported environment: {environment}")


# Instantiate the settings dynamically
settings = SettingsFactory.get_settings()
