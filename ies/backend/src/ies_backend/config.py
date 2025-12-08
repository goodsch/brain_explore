"""Application configuration."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = False

    # Neo4j
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "brainexplore"

    # Redis
    redis_url: str = "redis://localhost:6379"

    # SiYuan
    siyuan_host: str = "192.168.86.60"
    siyuan_port: int = 6806
    siyuan_token: str = "4we79so0hs4dmtlm"

    # Claude API (checks ANTHROPIC_API_KEY first, then IES_ANTHROPIC_API_KEY)
    anthropic_api_key: str = ""

    model_config = {"env_prefix": "IES_", "env_file": ".env"}

    def model_post_init(self, __context) -> None:
        """Fall back to ANTHROPIC_API_KEY if IES_ANTHROPIC_API_KEY not set."""
        import os
        if not self.anthropic_api_key:
            self.anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY", "")


settings = Settings()
