# Module: app.api.v1.news
# Description: Router handling economics news headlines feed and sentiment analysis logs.

from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.schemas.news import NewsItemResponseSchema, NewsSentimentResponseSchema
from app.services.news_service import NewsService

router = APIRouter(prefix="/news", tags=["News Sentiment"])


@router.get("/feed", response_model=List[NewsItemResponseSchema])
def get_news_feed(
    category: str = Query(None, description="Filter news by macroeconomic category"),
    sentiment: str = Query(None, description="Filter news by sentiment direction"),
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve news articles processed by NLP pipelines."""
    return NewsService.get_filtered_news(category, sentiment, db)


@router.get("/sentiment", response_model=NewsSentimentResponseSchema)
def get_sentiment_analysis(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve aggregate sentiment indicators of financial headlines."""
    return NewsService.get_aggregate_daily_sentiment(db)


@router.post("/ingest", response_model=dict)
def trigger_news_ingestion(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Trigger manual run of the news crawler and signal compilation pipeline."""
    from app.pipelines.news_ingest import NewsIngestionPipeline
    res = NewsIngestionPipeline.run_ingestion_cycle(db)
    return {"status": "success", "data": res}
