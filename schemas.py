from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


class ProductCreate(BaseModel):
    product_name: str
    category: Optional[str] = None
    description: Optional[str] = None


class BatchCreate(BaseModel):
    batch_id: str
    product_id: int
    manufacturing_date: Optional[date] = None
    expiry_date: Optional[date] = None


class StageCreate(BaseModel):
    batch_id: str
    stage_name: str
    stage_order: int
    description: Optional[str] = None
    timestamp: Optional[datetime] = None


class QualityCheckCreate(BaseModel):
    batch_id: str
    checked_by: str
    result: str
    remarks: Optional[str] = None
    checked_at: Optional[datetime] = None