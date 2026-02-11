"""Main orchestrator for SKU processing."""

import time
from typing import List
from ..api.replit_client import ReplitClient
from ..storage.state_manager import StateManager
from ..storage.models import ProcessingStatus, ProcessingResult, ProcessingReport
from .keyword_extractor import KeywordExtractor
from .image_validator import ImageValidator
from .image_search_service import ImageSearchService
from ..utils.logger import LoggerMixin
from ..utils.config import Config


class SKUProcessor(LoggerMixin):
    """Process SKUs to find and attach images."""

    def __init__(self, config: Config):
        """Initialize SKU processor."""
        self.config = config
        self.replit_client = ReplitClient(config.env.replit_api_url, config.env.replit_api_key)
        self.state_manager = StateManager(config.env.database_path)
        self.keyword_extractor = KeywordExtractor(**config.keywords_config)
        self.image_validator = ImageValidator(**config.validation_config)
        self.image_search = ImageSearchService(config)

    def process_all_skus(self) -> ProcessingReport:
        """Process all SKUs without images."""
        self.logger.info("Starting SKU processing batch")
        report = ProcessingReport()
        execution_id = self.state_manager.create_execution_record("manual")
        
        try:
            skus = self.replit_client.get_skus_without_images(limit=self.config.batch_size)
            report.total = len(skus)
            
            for sku in skus:
                result = self.process_single_sku(sku.id, sku.name)
                
                if result.success:
                    report.successful += 1
                    report.source_breakdown[result.image_source.value] = \
                        report.source_breakdown.get(result.image_source.value, 0) + 1
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
            
            image_data = self.replit_client.download_file(image_result.download_url)
            
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
                
        except Exception as e:
            error = str(e)
            self.logger.error(f"Error processing SKU {sku_id}: {error}", exc_info=True)
            self.state_manager.mark_sku_processed(sku_id, ProcessingStatus.FAILED, error=error)
            return ProcessingResult(sku_id=sku_id, success=False, error=error,
                                   processing_time=time.time() - start_time)
