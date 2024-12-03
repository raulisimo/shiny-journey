from unittest.mock import patch, MagicMock

import pytest

from config.settings import DevSettings, ProdSettings, SettingsFactory


@pytest.fixture
def mock_env_vars():
    """Mock environment variables."""
    with patch("os.getenv") as mock_getenv:
        mock_getenv.side_effect = lambda key, default=None: {
            "APP_TITLE": "Test App",
            "OMDB_API_KEY": "test_api_key",
            "DATABASE_URL": "sqlite:///test.db",
            "DEBUG": "true",
            "GCP_PROJECT_ID": "test-project",
            "DB_PASSWORD": "test-db-password",
            "CLOUD_SQL_CONNECTION_NAME": "test-connection-name",
            "DB_USER": "test-user",
            "DB_NAME": "test-database",
        }.get(key, default)
        yield mock_getenv


def test_dev_settings_initialization(mock_env_vars):
    settings = DevSettings()

    assert settings.APP_TITLE == "Test App"
    assert settings.OMDB_API_KEY == "test_api_key"
    assert settings.DATABASE_URL == "sqlite:///test.db"
    assert settings.DEBUG is True


def test_dev_settings_get_config_value(mock_env_vars):
    settings = DevSettings()

    assert settings.get_config_value("APP_TITLE") == "Test App"
    assert settings.get_config_value("OMDB_API_KEY") == "test_api_key"


def test_dev_settings_get_debug_mode(mock_env_vars):
    settings = DevSettings()

    assert settings.get_debug_mode() is True


@pytest.fixture
def mock_secret_manager_client():
    """Mock Google Secret Manager client."""
    with patch("config.settings.secretmanager.SecretManagerServiceClient") as mock_client:
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance

        def mock_access_secret_version(request):
            key = request["name"].split("/")[-3]
            secrets = {
                "APP_TITLE": "Test App",
                "OMDB_API_KEY": "test_api_key",
            }
            mock_response = MagicMock()
            mock_response.payload.data.decode.return_value = secrets.get(key, "default-secret-value")
            return mock_response

        mock_instance.access_secret_version.side_effect = mock_access_secret_version
        yield mock_instance


def test_prod_settings_initialization(mock_env_vars, mock_secret_manager_client):
    settings = ProdSettings()

    assert settings.gcp_project_id == "test-project"
    assert settings.APP_TITLE == "Test App"  # Mocks resolve secrets
    assert settings.OMDB_API_KEY == "test_api_key"


def test_prod_settings_get_config_value(mock_env_vars, mock_secret_manager_client):
    settings = ProdSettings()

    # Verify the value for OMDB_API_KEY
    secret_value = settings.get_config_value("OMDB_API_KEY")
    assert secret_value == "test_api_key"

    # Ensure the correct request was made for OMDB_API_KEY
    mock_secret_manager_client.access_secret_version.assert_any_call(
        request={"name": "projects/test-project/secrets/OMDB_API_KEY/versions/latest"}
    )

    # Assert total call count matches the secrets initialized
    assert mock_secret_manager_client.access_secret_version.call_count == 4


def test_settings_factory_dev(mock_env_vars):
    with patch("os.getenv", return_value="DEV"):
        settings = SettingsFactory.get_settings()
        assert isinstance(settings, DevSettings)


def test_settings_factory_invalid(mock_env_vars):
    with patch("os.getenv", return_value="INVALID"):
        with pytest.raises(ValueError, match="Unsupported environment: INVALID"):
            SettingsFactory.get_settings()


def test_dev_settings_get_db_connection(mock_env_vars):
    with patch("config.settings.create_engine") as mock_create_engine:
        settings = DevSettings()
        settings.get_db_connection()

        mock_create_engine.assert_called_once_with("sqlite:///test.db")
