from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Scrape.do configuration
    scrapedo_token: str = ""
    scrapedo_base_url: str = "http://api.scrape.do"
    
    # Database configuration
    database_url: str = "sqlite:///./data/scraper.db"
    
    # App configuration
    app_name: str = "Web Scraper"
    debug: bool = False
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
