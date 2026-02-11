"""Main orchestrator for SKU processing."""

import time
from typing import List
from pathlib import Path
from src.api.replit_client import ReplitClient
from src.storage.state_manager import StateManager
from src.storage.models import ProcessingStatus, ProcessingResult, ProcessingReport, SKU
from src.services.keyword_extractor import KeywordExtractor
from src.services.image_validator import ImageValidator
from src.services.image_search_service import ImageSearchService
from src.services.local_image_service import LocalImageService
from src.utils.logger import LoggerMixin
from src.utils.config import Config


class SKUProcessor(LoggerMixin):
    """Process SKUs to find and attach images."""

    def __init__(self, config: Config):
        """Initialize SKU processor."""
        self.config = config
        self.replit_client = ReplitClient(
            config.env.replit_api_url,
            config.env.replit_email,
            config.env.replit_password
        )
        self.state_manager = StateManager(config.env.database_path)
        self.keyword_extractor = KeywordExtractor(**config.keywords_config)
        self.image_validator = ImageValidator(**config.validation_config)
        self.image_search = ImageSearchService(config)

        # Initialize local image service if local_images_folder is configured
        self.use_local_images = hasattr(config.env, 'local_images_folder') and config.env.local_images_folder
        if self.use_local_images:
            self.local_image_service = LocalImageService(config.env.local_images_folder)
            self.logger.info(f"Using local images from: {config.env.local_images_folder}")
        else:
            self.local_image_service = None
            self.logger.info("Using API-based image search")

    def _load_skus_from_file(self, sku_file: str) -> List[SKU]:
        """Load SKU list from text file.

        Args:
            sku_file: Path to text file with SKU codes (one per line, # for comments)

        Returns:
            List of SKU objects
        """
        file_path = Path(sku_file)
        if not file_path.exists():
            raise FileNotFoundError(f"SKU file not found: {sku_file}")

        skus = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue

                # Create SKU object with just ID (name can be same as ID for local images)
                skus.append(SKU(id=line, name=line))

        self.logger.info(f"Loaded {len(skus)} SKUs from {sku_file}")
        return skus

    def process_all_skus(self, sku_file: str = None) -> ProcessingReport:
        """Process all SKUs without images.

        Args:
            sku_file: Optional path to text file containing SKU codes (one per line)
        """
        self.logger.info("Starting SKU processing batch")
        report = ProcessingReport()
        execution_id = self.state_manager.create_execution_record("manual")

        try:
            # Load SKUs from file if provided, otherwise use API
            if sku_file:
                skus = self._load_skus_from_file(sku_file)
            else:
                skus = self.replit_client.get_skus_without_images(limit=self.config.batch_size)

            report.total = len(skus)
            
            for sku in skus:
                result = self.process_single_sku(sku.id, sku.name)
                
                if result.success:
                    report.successful += 1
                    report.source_breakdown[result.image_source.value] = \
                        report.source_breakdown.get(result.image_source.value, 0) + 1
                elif result.error and "No suitable image found" in result.error:
                    report.needs_review += 1
                    report.error_summary.append(f"{sku.id}: {result.error}")
                elif result.error:
                    report.failed += 1
                    report.error_summary.append(f"{sku.id}: {result.error}")
                else:
                    report.skipped += 1
            
            report.completed_at = time.time()
            report.duration_seconds = time.time() - report.started_at.timestamp()
            
            self.state_manager.update_execution_record(
                execution_id, report.total, report.successful, report.failed, report.skipped
            )

            # Generate report file for SKUs needing manual review
            if report.needs_review > 0:
                from src.utils.report_writer import ReportWriter
                reports_cfg = self.config.reports_config if hasattr(self.config, 'reports_config') else {}
                output_dir = reports_cfg.get("output_dir", "./reports")

                writer = ReportWriter(output_dir=output_dir)
                needs_review_skus = self.state_manager.get_needs_review_skus()
                report_path = writer.write_needs_review_report(needs_review_skus)
                self.logger.info(f"Saved {len(needs_review_skus)} SKUs needing review to {report_path}")

            self.logger.info(f"Batch complete: {report.successful}/{report.total} successful")
            return report
            
        except Exception as e:
            self.logger.error(f"Batch processing failed: {e}", exc_info=True)
            raise

    def process_single_sku(self, sku_id: str, sku_name: str) -> ProcessingResult:
        """Process a single SKU."""
        start_time = time.time()
        self.logger.info(f"Processing SKU: {sku_id} ({sku_name})")

        if self.state_manager.is_sku_processed(sku_id):
            self.logger.info(f"SKU {sku_id} already processed, skipping")
            return ProcessingResult(sku_id=sku_id, success=False)

        try:
            # Use local images if configured
            if self.use_local_images:
                return self._process_with_local_image(sku_id, sku_name, start_time)
            else:
                return self._process_with_api_search(sku_id, sku_name, start_time)

        except Exception as e:
            error = str(e)
            self.logger.error(f"Error processing SKU {sku_id}: {error}", exc_info=True)
            self.state_manager.mark_sku_processed(sku_id, ProcessingStatus.FAILED, error=error)
            return ProcessingResult(sku_id=sku_id, success=False, error=error,
                                   processing_time=time.time() - start_time)

    def _process_with_local_image(self, sku_id: str, sku_name: str, start_time: float) -> ProcessingResult:
        """Process SKU using local image folder."""
        from src.storage.models import ImageSource

        # Find local image matching SKU
        local_image = self.local_image_service.find_image_for_sku(sku_id)

        if not local_image:
            error = f"No local image found for SKU: {sku_id}"
            self.logger.warning(f"SKU {sku_id}: {error}")
            self.state_manager.mark_sku_processed(sku_id, ProcessingStatus.NEEDS_REVIEW, error=error)
            return ProcessingResult(sku_id=sku_id, success=False, error=error,
                                   processing_time=time.time() - start_time)

        # Validate the local image
        validation = self.image_validator.validate_image(local_image.image_data)
        if not validation.is_valid:
            error = f"Image validation failed: {', '.join(validation.errors)}"
            self.logger.warning(f"SKU {sku_id}: {error}")
            self.state_manager.mark_sku_processed(sku_id, ProcessingStatus.FAILED, error=error)
            return ProcessingResult(sku_id=sku_id, success=False, error=error,
                                   processing_time=time.time() - start_time)

        # Upload to Replit
        success = self.replit_client.attach_image_to_sku(
            sku_id, local_image.image_data, local_image.filename
        )

        if success:
            self.state_manager.mark_sku_processed(
                sku_id, ProcessingStatus.SUCCESS, ImageSource.LOCAL,
                str(local_image.image_path), 1.0  # Perfect match score
            )
            self.logger.info(f"SKU {sku_id} processed successfully with local image")
            return ProcessingResult(
                sku_id=sku_id, success=True, image_attached=True,
                image_source=ImageSource.LOCAL, relevance_score=1.0,
                processing_time=time.time() - start_time
            )
        else:
            error = "Failed to attach image to SKU"
            self.state_manager.mark_sku_processed(sku_id, ProcessingStatus.FAILED, error=error)
            return ProcessingResult(sku_id=sku_id, success=False, error=error,
                                   processing_time=time.time() - start_time)

    def _process_with_api_search(self, sku_id: str, sku_name: str, start_time: float) -> ProcessingResult:
        """Process SKU using API-based image search (original logic)."""
        keywords = self.keyword_extractor.extract_keywords(sku_name)
        if not keywords:
            error = "No keywords extracted from SKU name"
            self.logger.warning(f"SKU {sku_id}: {error}")
            self.state_manager.mark_sku_processed(sku_id, ProcessingStatus.FAILED, error=error)
            return ProcessingResult(sku_id=sku_id, success=False, error=error,
                                   processing_time=time.time() - start_time)

        image_result = self.image_search.search_image(keywords)
        if not image_result:
            error = "No suitable image found"
            self.logger.warning(f"SKU {sku_id}: {error}")
            self.state_manager.mark_sku_processed(sku_id, ProcessingStatus.NEEDS_REVIEW, error=error)
            return ProcessingResult(sku_id=sku_id, success=False, error=error,
                                   processing_time=time.time() - start_time)

        # Download image from the source (Unsplash, Pexels, etc.)
        import requests
        response = requests.get(image_result.download_url, timeout=30)
        response.raise_for_status()
        image_data = response.content

        validation = self.image_validator.validate_image(image_data)
        if not validation.is_valid:
            error = f"Image validation failed: {', '.join(validation.errors)}"
            self.logger.warning(f"SKU {sku_id}: {error}")
            self.state_manager.mark_sku_processed(sku_id, ProcessingStatus.FAILED, error=error)
            return ProcessingResult(sku_id=sku_id, success=False, error=error,
                                   processing_time=time.time() - start_time)

        filename = f"{sku_id}.jpg"
        success = self.replit_client.attach_image_to_sku(sku_id, image_data, filename)

        if success:
            self.state_manager.mark_sku_processed(
                sku_id, ProcessingStatus.SUCCESS, image_result.source,
                image_result.url, image_result.relevance_score
            )
            self.logger.info(f"SKU {sku_id} processed successfully")
            return ProcessingResult(
                sku_id=sku_id, success=True, image_attached=True,
                image_source=image_result.source, relevance_score=image_result.relevance_score,
                processing_time=time.time() - start_time
            )
        else:
            error = "Failed to attach image to SKU"
            self.state_manager.mark_sku_processed(sku_id, ProcessingStatus.FAILED, error=error)
            return ProcessingResult(sku_id=sku_id, success=False, error=error,
                                   processing_time=time.time() - start_time)
