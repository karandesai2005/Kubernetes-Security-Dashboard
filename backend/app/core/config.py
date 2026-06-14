"""Application configuration via pydantic-settings."""
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Core
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/k8s_security"
    redis_url: str = "redis://localhost:6379/0"
    secret_key: str = "dev-secret-change-me"
    api_port: int = 8000

    # Feature flags
    enable_mock_data: bool = True
    enable_guardduty: bool = False

    # External
    aws_region: str = "us-east-1"
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    guardduty_detector_id: str = ""

    kubeconfig_path: str = "/etc/kubeconfig"
    k8s_namespace: str = "security-dashboard"

    falco_grpc_endpoint: str = "localhost:5060"

settings = Settings()
