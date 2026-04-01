from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from app.database.db import get_db
from app.database.models import ScrapeRecord
from app.models.schemas import (
    ScrapeRequest,
    ScrapeResponse,
    ScrapeResult,
    ArticleData,
    HistoryResponse,
    HistoryItem
)
from app.services.scraper import scrapedo_service
from app.services.parser import parse_html
from app.services.export import create_export_service

router = APIRouter()


@router.post("/scrape", response_model=ScrapeResponse)
async def scrape_url(request: ScrapeRequest, db: Session = Depends(get_db)):
    """
    Scrape a URL and extract content.
    
    - **url**: The URL to scrape
    - **extract_articles**: Whether to extract article content (default: true)
    - **extract_links**: Whether to extract all links (default: false)
    """
    try:
        # Call Scrape.do API
        result = await scrapedo_service.scrape(
            url=request.url,
            render_js=True  # Enable JS rendering for dynamic content
        )
        
        if not result['success']:
            # Save failed attempt
            record = ScrapeRecord(
                url=request.url,
                status="failed",
                error=result['error']
            )
            db.add(record)
            db.commit()
            
            return ScrapeResponse(
                success=False,
                message=f"Scraping failed: {result['error']}",
                data=None
            )
        
        # Parse HTML
        parser = parse_html(result['html'])
        
        articles = []
        if request.extract_articles:
            raw_articles = parser.extract_articles()
            articles = [ArticleData(**a) for a in raw_articles]
        
        # Save to database
        record = ScrapeRecord(
            url=request.url,
            status="success",
            articles=[a.model_dump() for a in articles],
            raw_html=result['html'][:50000] if result['html'] else None  # Limit stored HTML
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        
        scrape_result = ScrapeResult(
            id=record.id,
            url=request.url,
            status="success",
            scraped_at=record.scraped_at,
            articles=articles
        )
        
        return ScrapeResponse(
            success=True,
            message=f"Successfully scraped {len(articles)} articles",
            data=scrape_result
        )
        
    except Exception as e:
        # Log the error
        record = ScrapeRecord(
            url=request.url,
            status="error",
            error=str(e)
        )
        db.add(record)
        db.commit()
        
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history", response_model=HistoryResponse)
async def get_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get scraping history.
    
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return (1-100)
    """
    # Get total count
    total = db.query(ScrapeRecord).count()
    
    # Get records
    records = (
        db.query(ScrapeRecord)
        .order_by(ScrapeRecord.scraped_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    
    items = [
        HistoryItem(
            id=r.id,
            url=r.url,
            status=r.status,
            scraped_at=r.scraped_at,
            article_count=len(r.articles) if r.articles else 0
        )
        for r in records
    ]
    
    return HistoryResponse(
        success=True,
        items=items,
        total=total
    )


@router.get("/history/{record_id}")
async def get_record(record_id: int, db: Session = Depends(get_db)):
    """Get a specific scrape record by ID."""
    record = db.query(ScrapeRecord).filter(ScrapeRecord.id == record_id).first()
    
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    
    return {
        "success": True,
        "data": record.to_dict()
    }


@router.delete("/history/{record_id}")
async def delete_record(record_id: int, db: Session = Depends(get_db)):
    """Delete a scrape record by ID."""
    record = db.query(ScrapeRecord).filter(ScrapeRecord.id == record_id).first()
    
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    
    db.delete(record)
    db.commit()
    
    return {"success": True, "message": "Record deleted"}


@router.get("/export/{format}")
async def export_data(
    format: str,
    ids: Optional[str] = Query(None, description="Comma-separated list of IDs"),
    db: Session = Depends(get_db)
):
    """
    Export scraped data.
    
    - **format**: Export format (json or csv)
    - **ids**: Optional comma-separated list of record IDs to export
    """
    if format not in ['json', 'csv']:
        raise HTTPException(status_code=400, detail="Format must be 'json' or 'csv'")
    
    # Parse IDs if provided
    id_list = None
    if ids:
        try:
            id_list = [int(id.strip()) for id in ids.split(',')]
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid ID format")
    
    export_service = create_export_service(db)
    
    if format == 'json':
        content = export_service.export_to_json(id_list)
        return Response(
            content=content,
            media_type="application/json",
            headers={
                "Content-Disposition": f"attachment; filename=scrape_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            }
        )
    else:
        content = export_service.export_to_csv(id_list)
        return Response(
            content=content,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=scrape_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            }
        )
