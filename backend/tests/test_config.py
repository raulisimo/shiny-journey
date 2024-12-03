import os
from unittest.mock import patch, MagicMock

import pytest

from config.settings import DevSettings, ProdSettings, SettingsFactory, BaseSettings


# Test DevSettings
def test_dev_settings_env_vars(monkeypatch):
    """Test that DevSettings loads environment variables correctly."""
    # Mock environment variables
    monkeypatch.setenv("APP_TITLE", "Test App")
    monkeypatch.setenv("OMDB_API_KEY", "test-omdb-key")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///test.db")
    monkeypatch.setenv("JWT_SECRET", "test-secret")
    monkeypatch.setenv("DEBUG", "true")

    settings = DevSettings()

    assert settings.APP_TITLE == "Test App"
    assert settings.OMDB_API_KEY == "test-omdb-key"
    assert settings.DATABASE_URL == "sqlite:///test.db"
    assert settings.JWT_SECRET == "test-secret"
    assert settings.DEBUG is True


def test_dev_settings_missing_env_var(monkeypatch):
    """Test that DevSettings raises an error for missing environment variables."""
    monkeypatch.delenv("APP_TITLE", raising=False)  # Ensure the variable is unset

    with pytest.raises(ValueError, match="Missing required configuration: APP_TITLE"):
        DevSettings()


# Test ProdSettings
@patch("config.settings.secretmanager.SecretManagerServiceClient")
def test_prod_settings(mock_secret_manager_client):
    """Test that ProdSettings fetches secrets from Google Secret Manager."""
    # Mock the secret manager response
    mock_client = MagicMock()
    mock_secret_manager_client.return_value = mock_client
    mock_client.access_secret_version.return_value.payload.data.decode.return_value = "mocked-value"

    # Set required GCP_PROJECT_ID
    with patch.dict(os.environ, {"GCP_PROJECT_ID": "test-project"}):
        settings = ProdSettings()

        # Mock access to a specific secret
        assert settings.get_config_value("APP_TITLE") == "mocked-value"
        mock_client.access_secret_version.assert_called_once_with(
            request={"name": "projects/test-project/secrets/APP_TITLE/versions/latest"}
        )


def test_prod_settings_missing_gcp_project_id():
    """Test that ProdSettings raises an error if GCP_PROJECT_ID is missing."""
    with patch.dict(os.environ, {}, clear=True):  # Clear all environment variables
        with pytest.raises(ValueError, match="Missing required GCP_PROJECT_ID for production"):
            ProdSettings()


# Test SettingsFactory
def test_settings_factory_dev(monkeypatch):
    """Test that SettingsFactory returns DevSettings for DEV environment."""
    monkeypatch.setenv("ENV", "DEV")
    settings = SettingsFactory.get_settings()
    assert isinstance(settings, DevSettings)


def test_settings_factory_prod(monkeypatch):
    """Test that SettingsFactory returns ProdSettings for PRO environment."""
    monkeypatch.setenv("ENV", "PRO")
    with patch("config.settings.secretmanager.SecretManagerServiceClient"):
        settings = SettingsFactory.get_settings()
        assert isinstance(settings, ProdSettings)


def test_settings_factory_invalid_env(monkeypatch):
    """Test that SettingsFactory raises an error for unsupported environments."""
    monkeypatch.setenv("ENV", "INVALID")
    with pytest.raises(ValueError, match="Unsupported environment: INVALID"):
        SettingsFactory.get_settings()


# BaseSettings cannot be instantiated directly
def test_base_settings_not_implemented():
    """Test that BaseSettings raises NotImplementedError for abstract methods."""
    with pytest.raises(TypeError):
        BaseSettings()  # Cannot instantiate abstract class

    class TestSettings(BaseSettings):
        def get_config_value(self, key: str) -> str:
            return "test"

    settings = TestSettings()
    assert settings.get_debug_mode() is False
