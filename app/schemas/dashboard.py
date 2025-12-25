from typing import Optional
from pydantic import BaseModel
from .damage_record import DamageDistribution
from .prediction import PredictionResponse

class DashboardStats(BaseModel):
    """Schema for dashboard statistics."""
    total_components: int
    total_damage_records: int
    total_predictions: int
    damage_distribution: DamageDistribution
    recent_predictions: list[PredictionResponse]
    model_accuracy: Optional[float] = None
    is_model_trained: bool = False