# Module: app.services.news_service
# Description: Service handling financial news query filters and sentiment aggregate compilations.

import uuid
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.news import NewsItem


class NewsService:
    @staticmethod
    def get_mock_news():
        """Get realistic mock news matching frontend configuration."""
        base_time = datetime(2026, 6, 7, 10, 0, 0)
        items = [
            {
                "id": uuid.UUID("1a111111-1111-1111-1111-111111111111"),
                "headline": "Central Bank retains policy repo rate at 6.50% to align inflation back to 4.0% target",
                "source": "Financial Bulletin",
                "published_at": base_time - timedelta(hours=2),
                "sentiment": "Bullish",
                "impact_score": 78.0,
                "category": "Monetary Policy",
                "url": "https://financialbulletin.ai/repo-rate-june-2026"
            },
            {
                "id": uuid.UUID("2b222222-2222-2222-2222-222222222222"),
                "headline": "Crude oil prices decline below $78 per barrel amid supply increase reports",
                "source": "Global Market Monitor",
                "published_at": base_time - timedelta(hours=4),
                "sentiment": "Bullish",
                "impact_score": 85.0,
                "category": "Commodities",
                "url": "https://globalmonitor.ai/crude-oil-drops"
            },
            {
                "id": uuid.UUID("3c333333-3333-3333-3333-333333333333"),
                "headline": "El Niño weather pattern threatens local crop yields; Pulse and Veg pricing expected to rise",
                "source": "Agricultural Times",
                "published_at": base_time - timedelta(days=1),
                "sentiment": "Bearish",
                "impact_score": 92.0,
                "category": "Agriculture",
                "url": "https://agri-times.ai/el-nino-impact"
            },
            {
                "id": uuid.UUID("4d444444-4444-4444-4444-444444444444"),
                "headline": "Local currency gains strength against USD, easing pressure on import costs of key electronics",
                "source": "FX Journal",
                "published_at": base_time - timedelta(days=1),
                "sentiment": "Bullish",
                "impact_score": 68.0,
                "category": "Currency",
                "url": "https://fxjournal.ai/usd-inr-dipped"
            },
            {
                "id": uuid.UUID("5e555555-5555-5555-5555-555555555555"),
                "headline": "Supply chain disruptions reported at key shipping terminals due to port maintenance scheduling",
                "source": "Logistics Weekly",
                "published_at": base_time - timedelta(days=2),
                "sentiment": "Neutral",
                "impact_score": 45.0,
                "category": "Supply Chain",
                "url": "https://logistics-weekly.ai/terminal-maintenance"
            }
        ]
        return items

    @staticmethod
    def get_filtered_news(category: str | None, sentiment: str | None, db: Session):
        """Retrieve news matches satisfying category and sentiment filters."""
        query = db.query(NewsItem)
        if category:
            query = query.filter(NewsItem.category.ilike(category))
        if sentiment:
            query = query.filter(NewsItem.sentiment.ilike(sentiment))
        
        db_news = query.order_by(NewsItem.published_at.desc()).all()
        if db_news:
            return db_news
        
        # Fallback filter mock data
        mock_news = NewsService.get_mock_news()
        filtered = []
        for item in mock_news:
            if category and item["category"].lower() != category.lower():
                continue
            if sentiment and item["sentiment"].lower() != sentiment.lower():
                continue
            filtered.append(item)
        return filtered

    @staticmethod
    def get_aggregate_daily_sentiment(db: Session):
        """Compile and average overall daily economic news sentiment metrics."""
        # 1. DB First Strategy: Query news_signals and news_items tables
        try:
            from app.models.news import NewsSignal
            latest_signal = db.query(NewsSignal).order_by(NewsSignal.recording_date.desc()).first()
            if latest_signal:
                today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
                stats = db.query(
                    func.avg(NewsItem.impact_score).label("avg_impact"),
                    NewsItem.sentiment,
                    func.count(NewsItem.id).label("count")
                ).filter(NewsItem.published_at >= today_start).group_by(NewsItem.sentiment).all()
                
                counts = {"Bullish": 0, "Bearish": 0, "Neutral": 0}
                total_impact = 0.0
                total_count = 0
                
                for row in stats:
                    sent_key = row[1].title() if row[1] else "Neutral"
                    if sent_key == "Positive":
                        sent_key = "Bullish"
                    elif sent_key == "Negative":
                        sent_key = "Bearish"
                    
                    counts[sent_key] = row[2]
                    total_count += row[2]
                    total_impact += (row[0] or 0.0) * row[2]
                    
                avg_impact = round(total_impact / total_count, 2) if total_count > 0 else 0.0
                
                regional_impact = {}
                todays_items = db.query(NewsItem).filter(NewsItem.published_at >= today_start).all()
                for item in todays_items:
                    if item.regional_impact:
                        for loc, count in item.regional_impact.items():
                            regional_impact[loc] = regional_impact.get(loc, 0) + count
                            
                topic_trends = {}
                if latest_signal.topic_volumes:
                    for topic, vol in latest_signal.topic_volumes.items():
                        topic_trends[topic] = float(vol)
                        
                return {
                    "average_impact_score": avg_impact,
                    "sentiment_counts": counts,
                    "sentiment_score": latest_signal.avg_sentiment,
                    "economic_risk_score": latest_signal.risk_score,
                    "inflation_pressure_score": latest_signal.inflation_pressure,
                    "topic_trends": topic_trends,
                    "regional_impact": regional_impact
                }
        except Exception as e:
            print(f"Database query failed in NewsService.get_aggregate_daily_sentiment: {e}")

        # 2. Fallback mock data stats
        mock_news = NewsService.get_mock_news()
        total_impact = sum(item["impact_score"] for item in mock_news)
        avg_impact = round(total_impact / len(mock_news), 2)
        
        counts = {"Bullish": 0, "Bearish": 0, "Neutral": 0}
        for item in mock_news:
            counts[item["sentiment"]] = counts.get(item["sentiment"], 0) + 1
        
        return {
            "average_impact_score": avg_impact,
            "sentiment_counts": counts,
            "sentiment_score": 0.45,
            "economic_risk_score": 1.25,
            "inflation_pressure_score": 2.10,
            "topic_trends": {
                "Monetary Policy": 12.0,
                "Commodity Shocks": 8.0,
                "Food & Agriculture": 5.0,
                "Supply Chain & Logistics": 4.0,
                "Currency & Exchange Rates": 2.0
            },
            "regional_impact": {
                "Delhi": 3,
                "Maharashtra": 2,
                "Gujarat": 1
            }
        }
