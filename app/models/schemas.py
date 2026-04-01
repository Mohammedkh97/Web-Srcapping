from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, List
from datetime import datetime


class ScrapeRequest(BaseModel):
    """Request model for scraping a URL."""
    url: str = Field(..., description="URL to scrape")
    extract_articles: bool = Field(default=True, description="Extract article content")
    extract_links: bool = Field(default=False, description="Extract all links")


class ArticleData(BaseModel):
    """Model for extracted article data."""
    title: Optional[str] = None
    content: Optional[str] = None
    excerpt: Optional[str] = None
    author: Optional[str] = None
    date: Optional[str] = None
    url: Optional[str] = None
    image_url: Optional[str] = None
    category: Optional[str] = None


class ScrapeResult(BaseModel):
    """Model for scraping result."""
    id: Optional[int] = None
    url: str
    status: str
    scraped_at: datetime
    articles: List[ArticleData] = []
    raw_html: Optional[str] = None
    error: Optional[str] = None


class ScrapeResponse(BaseModel):
    """API response for scrape request."""
    success: bool
    message: str
    data: Optional[ScrapeResult] = None


class HistoryItem(BaseModel):
    """Model for history list item."""
    id: int
    url: str
    status: str
    scraped_at: datetime
    article_count: int


class HistoryResponse(BaseModel):
    """API response for history request."""
    success: bool
    items: List[HistoryItem] = []
    total: int = 0


class ExportRequest(BaseModel):
    """Request model for export."""
    format: str = Field(default="json", description="Export format: json or csv")
    ids: Optional[List[int]] = Field(default=None, description="Specific IDs to export")
