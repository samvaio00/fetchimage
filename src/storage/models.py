"""Data models using Pydantic."""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl


class ProcessingStatus(str, Enum):
    """Status of SKU processing."""

    SUCCESS = "success"
    FAILED = "failed"
    NEEDS_REVIEW = "needs_review"
    PENDING = "pending"


class ImageSource(str, Enum):
    """Image source types."""

    FREEPIK = "freepik"
    PEXELS = "pexels"
    PIXABAY = "pixabay"
    WEB_SCRAPER = "web_scraper"
    MANUAL = "manual"


class SKU(BaseModel):
    """SKU/Product model."""

    id: str = Field(..., description="Unique SKU identifier")
    name: str = Field(..., description="SKU name")
    description: Optional[str] = Field(None, description="SKU description")
    category: Optional[str] = Field(None, description="Product category")
    has_image: bool = Field(False, description="Whether SKU has an image")

    class Config:
        """Pydantic config."""

        from_attributes = True


class ImageResult(BaseModel):
    """Image search result."""

    id: str = Field(..., description="Image ID from source")
    url: str = Field(..., description="Image URL")
    download_url: str = Field(..., description="Direct download URL")
    source: ImageSource = Field(..., description="Image source")
    title: Optional[str] = Field(None, description="Image title/description")
    width: int = Field(..., description="Image width in pixels")
    height: int = Field(..., description="Image height in pixels")
    file_size: Optional[int] = Field(None, description="File size in bytes")
    relevance_score: float = Field(0.0, description="Relevance score (0-1)")
    photographer: Optional[str] = Field(None, description="Photographer name")
    photographer_url: Optional[str] = Field(None, description="Photographer URL")

    @property
    def aspect_ratio(self) -> float:
        """Calculate aspect ratio."""
        return self.width / self.height if self.height > 0 else 0.0

    class Config:
        """Pydantic config."""

        from_attributes = True


class ValidationResult(BaseModel):
    """Image validation result."""

    is_valid: bool = Field(..., description="Whether image is valid")
    errors: List[str] = Field(default_factory=list, description="Validation errors")
    warnings: List[str] = Field(
        default_factory=list, description="Validation warnings"
    )
    format: Optional[str] = Field(None, description="Image format")
    width: Optional[int] = Field(None, description="Image width")
    height: Optional[int] = Field(None, description="Image height")
    file_size: Optional[int] = Field(None, description="File size in bytes")
    aspect_ratio: Optional[float] = Field(None, description="Aspect ratio")

    class Config:
        """Pydantic config."""

        from_attributes = True


class ProcessingRecord(BaseModel):
    """Record of SKU processing attempt."""

    id: Optional[int] = Field(None, description="Record ID")
    sku_id: str = Field(..., description="SKU identifier")
    status: ProcessingStatus = Field(..., description="Processing status")
    image_source: Optional[ImageSource] = Field(None, description="Image source")
    image_url: Optional[str] = Field(None, description="Image URL")
    relevance_score: Optional[float] = Field(None, description="Relevance score")
    processed_at: datetime = Field(
        default_factory=datetime.utcnow, description="Processing timestamp"
    )
    attempts: int = Field(1, description="Number of attempts")
    last_error: Optional[str] = Field(None, description="Last error message")
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="Creation timestamp"
    )

    class Config:
        """Pydantic config."""

        from_attributes = True


class ProcessingResult(BaseModel):
    """Result of processing a single SKU."""

    sku_id: str = Field(..., description="SKU identifier")
    success: bool = Field(..., description="Whether processing was successful")
    image_attached: bool = Field(False, description="Whether image was attached")
    image_source: Optional[ImageSource] = Field(None, description="Image source used")
    relevance_score: Optional[float] = Field(None, description="Image relevance score")
    error: Optional[str] = Field(None, description="Error message if failed")
    processing_time: float = Field(0.0, description="Processing time in seconds")

    class Config:
        """Pydantic config."""

        from_attributes = True


class ProcessingReport(BaseModel):
    """Summary report of processing session."""

    total: int = Field(0, description="Total SKUs processed")
    successful: int = Field(0, description="Successfully processed")
    failed: int = Field(0, description="Failed to process")
    skipped: int = Field(0, description="Skipped (already processed)")
    needs_review: int = Field(0, description="Needs manual review")
    started_at: datetime = Field(
        default_factory=datetime.utcnow, description="Session start time"
    )
    completed_at: Optional[datetime] = Field(None, description="Session completion time")
    duration_seconds: float = Field(0.0, description="Total duration in seconds")
    source_breakdown: dict = Field(
        default_factory=dict, description="Breakdown by image source"
    )
    error_summary: List[str] = Field(
        default_factory=list, description="Summary of errors"
    )

    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        if self.total == 0:
            return 0.0
        return (self.successful / self.total) * 100

    class Config:
        """Pydantic config."""

        from_attributes = True


class ExecutionHistory(BaseModel):
    """Record of a complete execution."""

    id: Optional[int] = Field(None, description="Execution ID")
    started_at: datetime = Field(
        default_factory=datetime.utcnow, description="Start time"
    )
    completed_at: Optional[datetime] = Field(None, description="Completion time")
    total_skus: int = Field(0, description="Total SKUs processed")
    successful: int = Field(0, description="Successfully processed")
    failed: int = Field(0, description="Failed to process")
    skipped: int = Field(0, description="Skipped SKUs")
    duration_seconds: Optional[int] = Field(None, description="Duration in seconds")
    trigger_type: str = Field("manual", description="How execution was triggered")

    class Config:
        """Pydantic config."""

        from_attributes = True
