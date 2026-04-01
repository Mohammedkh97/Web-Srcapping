from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.sql import func
from app.database.db import Base


class ScrapeRecord(Base):
    """SQLAlchemy model for scrape records."""
    __tablename__ = "scrape_records"
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(2048), nullable=False, index=True)
    status = Column(String(50), default="pending")
    scraped_at = Column(DateTime(timezone=True), server_default=func.now())
    articles = Column(JSON, default=[])
    raw_html = Column(Text, nullable=True)
    error = Column(Text, nullable=True)
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "url": self.url,
            "status": self.status,
            "scraped_at": self.scraped_at.isoformat() if self.scraped_at else None,
            "articles": self.articles or [],
            "error": self.error
        }
    
    def article_count(self):
        """Get the number of articles."""
        return len(self.articles) if self.articles else 0
