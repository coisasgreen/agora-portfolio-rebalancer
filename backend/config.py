"""Configuration module."""

import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings from environment."""
    
    # Arc Network
    arc_rpc_url: str = os.getenv("ARC_RPC_URL", "https://testnet.arc.network")
    arc_chain_id: int = int(os.getenv("ARC_CHAIN_ID", "2025"))
    
    # Database
    database_url: str = os.getenv("DATABASE_URL", "postgresql://localhost:5432/agora")
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # API
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "5000"))
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Security
    secret_key: str = os.getenv("SECRET_KEY", "change-me-in-production")
    jwt_algorithm: str = "HS256"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
