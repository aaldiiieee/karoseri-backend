import logging
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..configs.db import get_db
from ..schemas import DashboardStats
from ..services import (
    component_service,
    damage_record_service,
    prediction_service,
    model_metrics_service,
    naive_bayes_service
)

logger = logging.getLogger("app")

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(db: AsyncSession = Depends(get_db)):
    """Get dashboard statistics."""
    logger.debug("Getting dashboard stats")
    
    # Get counts
    total_components = await component_service.get_count(db)
    total_damage_records = await damage_record_service.get_count(db)
    total_predictions = await prediction_service.get_count(db)
    
    # Get damage distribution
    damage_distribution = await damage_record_service.get_distribution(db)
    
    # Get recent predictions
    recent_predictions = await prediction_service.get_recent(db, limit=5)
    
    # Get model accuracy
    latest_metrics = await model_metrics_service.get_latest(db)
    model_accuracy = latest_metrics.accuracy if latest_metrics else None
    
    return DashboardStats(
        total_components=total_components,
        total_damage_records=total_damage_records,
        total_predictions=total_predictions,
        damage_distribution=damage_distribution,
        recent_predictions=recent_predictions,
        model_accuracy=model_accuracy,
        is_model_trained=naive_bayes_service.is_trained
    )