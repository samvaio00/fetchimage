"""Validate images before uploading."""

from io import BytesIO
from typing import List
from PIL import Image
from ..storage.models import ValidationResult
from ..utils.logger import LoggerMixin


class ImageValidator(LoggerMixin):
    """Validate image format, dimensions, and quality."""

    def __init__(self, min_width: int = 800, min_height: int = 600,
                 max_file_size_mb: int = 5, allowed_formats: List[str] = None,
                 min_aspect_ratio: float = 0.5, max_aspect_ratio: float = 2.0):
        """Initialize image validator."""
        self.min_width = min_width
        self.min_height = min_height
        self.max_file_size = max_file_size_mb * 1024 * 1024
        self.allowed_formats = allowed_formats or ["JPEG", "PNG", "WebP"]
        self.min_aspect_ratio = min_aspect_ratio
        self.max_aspect_ratio = max_aspect_ratio

    def validate_image(self, image_data: bytes) -> ValidationResult:
        """Validate image data."""
        errors = []
        warnings = []
        
        file_size = len(image_data)
        if file_size > self.max_file_size:
            errors.append(f"File size {file_size/1024/1024:.2f}MB exceeds max {self.max_file_size/1024/1024}MB")
        
        try:
            img = Image.open(BytesIO(image_data))
            img_format = img.format
            width, height = img.size
            aspect_ratio = width / height if height > 0 else 0
            
            if img_format not in self.allowed_formats:
                errors.append(f"Format {img_format} not in allowed formats: {self.allowed_formats}")
            
            if width < self.min_width or height < self.min_height:
                errors.append(f"Dimensions {width}x{height} below minimum {self.min_width}x{self.min_height}")
            
            if aspect_ratio < self.min_aspect_ratio or aspect_ratio > self.max_aspect_ratio:
                warnings.append(f"Aspect ratio {aspect_ratio:.2f} outside recommended range")
            
            return ValidationResult(
                is_valid=len(errors) == 0,
                errors=errors,
                warnings=warnings,
                format=img_format,
                width=width,
                height=height,
                file_size=file_size,
                aspect_ratio=aspect_ratio
            )
        
        except Exception as e:
            errors.append(f"Failed to process image: {str(e)}")
            return ValidationResult(is_valid=False, errors=errors, warnings=warnings)
