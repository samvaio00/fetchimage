"""Service for handling local image files matched by SKU."""

import os
from pathlib import Path
from typing import Optional, Dict
from src.utils.logger import LoggerMixin


class LocalImageResult:
    """Result of local image lookup."""

    def __init__(self, sku: str, image_path: Path, image_data: bytes):
        self.sku = sku
        self.image_path = image_path
        self.image_data = image_data
        self.filename = image_path.name


class LocalImageService(LoggerMixin):
    """Service to match SKUs with local image files.

    Expected folder structure:
        images/
            SKU123.jpg
            SKU456.png
            SKU789.webp

    Filenames (without extension) must match the SKU code.
    """

    def __init__(self, images_folder: str):
        """Initialize local image service.

        Args:
            images_folder: Path to folder containing SKU images
        """
        self.images_folder = Path(images_folder)
        self.supported_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']

        if not self.images_folder.exists():
            raise ValueError(f"Images folder does not exist: {images_folder}")

        if not self.images_folder.is_dir():
            raise ValueError(f"Images path is not a directory: {images_folder}")

        self.logger.info(f"Initialized LocalImageService with folder: {images_folder}")
        self._build_sku_index()

    def _build_sku_index(self) -> None:
        """Build index of available SKU images for faster lookup."""
        self.sku_index: Dict[str, Path] = {}

        for ext in self.supported_extensions:
            for image_path in self.images_folder.glob(f"*{ext}"):
                # Get SKU from filename (without extension)
                sku = image_path.stem

                # Store case-insensitive for matching
                sku_lower = sku.lower()

                # Keep first match if duplicate (warn user)
                if sku_lower in self.sku_index:
                    self.logger.warning(
                        f"Duplicate SKU image found: {sku} "
                        f"(keeping {self.sku_index[sku_lower].name}, ignoring {image_path.name})"
                    )
                else:
                    self.sku_index[sku_lower] = image_path

        self.logger.info(f"Indexed {len(self.sku_index)} SKU images")

    def find_image_for_sku(self, sku: str) -> Optional[LocalImageResult]:
        """Find local image file matching the SKU.

        Args:
            sku: SKU code to search for (case-insensitive)

        Returns:
            LocalImageResult if found, None otherwise
        """
        sku_lower = sku.lower()

        if sku_lower not in self.sku_index:
            self.logger.debug(f"No local image found for SKU: {sku}")
            return None

        image_path = self.sku_index[sku_lower]

        try:
            with open(image_path, 'rb') as f:
                image_data = f.read()

            self.logger.info(f"Found local image for SKU {sku}: {image_path.name}")
            return LocalImageResult(sku, image_path, image_data)

        except Exception as e:
            self.logger.error(f"Failed to read image file {image_path}: {e}")
            return None

    def get_available_skus(self) -> list[str]:
        """Get list of all SKUs that have local images.

        Returns:
            List of SKU codes (original case from filename)
        """
        return [path.stem for path in self.sku_index.values()]

    def refresh_index(self) -> None:
        """Refresh the SKU index (useful if files were added/removed)."""
        self.logger.info("Refreshing SKU image index")
        self._build_sku_index()
