import json
import csv
import io
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.database.models import ScrapeRecord


class ExportService:
    """Service for exporting scraped data."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def export_to_json(self, ids: Optional[List[int]] = None) -> str:
        """
        Export records to JSON format.
        
        Args:
            ids: Optional list of record IDs to export. If None, exports all.
            
        Returns:
            JSON string of the exported data
        """
        records = self._get_records(ids)
        
        export_data = {
            "exported_at": datetime.utcnow().isoformat(),
            "total_records": len(records),
            "records": []
        }
        
        for record in records:
            export_data["records"].append({
                "id": record.id,
                "url": record.url,
                "status": record.status,
                "scraped_at": record.scraped_at.isoformat() if record.scraped_at else None,
                "articles": record.articles or [],
                "article_count": len(record.articles) if record.articles else 0
            })
        
        return json.dumps(export_data, indent=2, ensure_ascii=False)
    
    def export_to_csv(self, ids: Optional[List[int]] = None) -> str:
        """
        Export records to CSV format.
        
        Args:
            ids: Optional list of record IDs to export. If None, exports all.
            
        Returns:
            CSV string of the exported data
        """
        records = self._get_records(ids)
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'Record ID',
            'URL',
            'Status',
            'Scraped At',
            'Article Title',
            'Article URL',
            'Article Excerpt',
            'Article Date',
            'Article Author',
            'Article Category'
        ])
        
        # Write data rows
        for record in records:
            if record.articles:
                for article in record.articles:
                    writer.writerow([
                        record.id,
                        record.url,
                        record.status,
                        record.scraped_at.isoformat() if record.scraped_at else '',
                        article.get('title', ''),
                        article.get('url', ''),
                        article.get('excerpt', '')[:200] if article.get('excerpt') else '',
                        article.get('date', ''),
                        article.get('author', ''),
                        article.get('category', '')
                    ])
            else:
                # Write record even if no articles
                writer.writerow([
                    record.id,
                    record.url,
                    record.status,
                    record.scraped_at.isoformat() if record.scraped_at else '',
                    '', '', '', '', '', ''
                ])
        
        return output.getvalue()
    
    def _get_records(self, ids: Optional[List[int]] = None) -> List[ScrapeRecord]:
        """Get records from database."""
        query = self.db.query(ScrapeRecord)
        
        if ids:
            query = query.filter(ScrapeRecord.id.in_(ids))
        
        return query.order_by(ScrapeRecord.scraped_at.desc()).all()


def create_export_service(db: Session) -> ExportService:
    """Create an export service instance."""
    return ExportService(db)
