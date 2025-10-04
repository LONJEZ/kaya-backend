from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import date, datetime


# Analytics Models
class AnalyticsOverview(BaseModel):
    total_revenue: float
    total_expenses: float
    profit_margin: float
    top_product: Optional[str] = None
    period: str  # e.g., "last_30_days"


class RevenueTrend(BaseModel):
    month: str
    revenue: float


class TopProduct(BaseModel):
    name: str
    category: str
    sales: float
    quantity: int


class Transaction(BaseModel):
    id: str
    date: str
    item: str
    amount: float
    method: str


# Chat Models
class ChatQuery(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    user_id: str


class ChatResponse(BaseModel):
    answer_text: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    visualization: Optional[Dict[str, Any]] = None
    structured: Optional[Dict[str, Any]] = None
    sources: Optional[List[str]] = None


# Settings Models
class UserSettings(BaseModel):
    currency: str = "KES"
    language: str = "en"
    refresh_frequency: str = "hourly"

class IngestionStatus(BaseModel):
    ingestion_id: str
    status: str  # processing, completed, failed
    rows_uploaded: int
    rows_processed: Optional[int] = None
    rows_skipped: Optional[int] = None
    message: Optional[str] = None
    error: Optional[str] = None


class DataSourceConfig(BaseModel):
    source_type: str  # sheets, mpesa, pos
    credentials: Optional[Dict[str, Any]] = None
    config: Optional[Dict[str, Any]] = None


class ConnectorConfig(BaseModel):
    source_id: str
    type: str  # sheets, mpesa, pos
    spreadsheet_id: Optional[str] = None
    sheet_name: Optional[str] = None
    credentials_path: Optional[str] = None
    csv_data: Optional[str] = None
    config: Optional[Dict[str, Any]] = None


class ConnectorStatus(BaseModel):
    source_id: str
    status: str  # connected, syncing, synced, error
    message: Optional[str] = None
    last_sync: Optional[str] = None
    state: Optional[Dict[str, Any]] = None


class SyncRequest(BaseModel):
    source_id: str
    force_full_sync: bool = False


class CategorySales(BaseModel):
    category: str
    sales: float
    count: int


class AnalyticsOverview(BaseModel):
    total_revenue: float
    total_expenses: float
    profit_margin: float
    top_product: Optional[str] = None
    revenue_growth: Optional[float] = None
    period: str



