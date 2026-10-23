from fastapi import APIRouter, Depends
from src.services.behavior_service import BehaviorService
from pydantic import BaseModel
import matplotlib.pyplot as plt
from io import BytesIO
import base64

router = APIRouter()

class BehaviorData(BaseModel):
    student_id: int
    behavior: list
    dates: list

@router.post("/behavior_trend")
async def get_behavior_trend(data: BehaviorData, behavior_service: BehaviorService = Depends()):
    plot_url = behavior_service.generate_behavior_plot(data.student_id)
    return {"plot_url": plot_url}
