"""Generate text reports for SKUs needing manual review."""

from datetime import datetime
from pathlib import Path
from typing import List, Optional

from ..storage.models import ProcessingRecord
from .logger import LoggerMixin


class ReportWriter(LoggerMixin):
    """Write reports for SKUs that need manual intervention."""

    def __init__(self, output_dir: str = "./reports"):
        """Initialize report writer."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logger.info(f"Report writer initialized. Output dir: {self.output_dir}")

    def write_needs_review_report(
        self,
        skus: List[ProcessingRecord],
        filename: Optional[str] = None
    ) -> str:
        """Write SKUs needing manual review to text file."""
        if not skus:
            self.logger.info("No SKUs need review, skipping report generation")
            return ""

        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"needs_review_{timestamp}.txt"

        filepath = self.output_dir / filename
        self.logger.info(f"Writing needs_review report to {filepath}")

        with open(filepath, "w", encoding="utf-8") as f:
            f.write("SKUs Requiring Manual Review - Image Not Found\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Total SKUs Needing Review: {len(skus)}\n\n")

            f.write(f"{'SKU ID':<25} | {'Processed At':<20} | {'Last Error':<30}\n")
            f.write("-" * 25 + " | " + "-" * 20 + " | " + "-" * 30 + "\n")

            for sku in skus:
                sku_id = sku.sku_id[:24] if len(sku.sku_id) > 24 else sku.sku_id
                processed_at = sku.processed_at.strftime('%Y-%m-%d %H:%M:%S')
                error = (sku.last_error or "Unknown error")[:29]

                f.write(f"{sku_id:<25} | {processed_at:<20} | {error:<30}\n")

            f.write("\n" + "=" * 80 + "\n\n")
            f.write("Next Steps:\n")
            f.write("1. Review SKU names for clarity and searchability\n")
            f.write("2. Manually source images for these products\n")
            f.write("3. Update SKU database with better keywords/descriptions\n")
            f.write("4. Re-run bot after making changes\n")

        self.logger.info(f"Report written successfully: {filepath}")
        return str(filepath)
