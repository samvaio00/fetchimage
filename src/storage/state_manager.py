"""SQLite-based state management for tracking processed SKUs."""

import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

from src.utils.logger import LoggerMixin
from src.storage.models import ExecutionHistory, ProcessingRecord, ProcessingStatus, ImageSource


class StateManager(LoggerMixin):
    """Manage processing state using SQLite database."""

    def __init__(self, db_path: str = "./data/state.db"):
        """Initialize state manager."""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        """Initialize database schema."""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Create processed_skus table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS processed_skus (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sku_id TEXT UNIQUE NOT NULL,
                status TEXT NOT NULL,
                image_source TEXT,
                image_url TEXT,
                relevance_score REAL,
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                attempts INTEGER DEFAULT 1,
                last_error TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS processing_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                sku_id TEXT,
                action TEXT,
                details TEXT,
                level TEXT
            )
        """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS execution_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                total_skus INTEGER,
                successful INTEGER,
                failed INTEGER,
                skipped INTEGER,
                duration_seconds INTEGER,
                trigger_type TEXT
            )
        """
        )

        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sku_id ON processed_skus(sku_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_status ON processed_skus(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_processed_at ON processed_skus(processed_at)")

        conn.commit()
        conn.close()
        self.logger.info(f"Database initialized at {self.db_path}")

    def is_sku_processed(self, sku_id: str) -> bool:
        """Check if SKU has been successfully processed."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT status FROM processed_skus WHERE sku_id = ? AND status = ?",
                      (sku_id, ProcessingStatus.SUCCESS.value))
        result = cursor.fetchone()
        conn.close()
        return result is not None

    def mark_sku_processed(self, sku_id: str, status: ProcessingStatus,
                          image_source: Optional[ImageSource] = None,
                          image_url: Optional[str] = None,
                          relevance_score: Optional[float] = None,
                          error: Optional[str] = None) -> None:
        """Mark SKU as processed with status."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, attempts FROM processed_skus WHERE sku_id = ?", (sku_id,))
        existing = cursor.fetchone()

        if existing:
            attempts = existing["attempts"] + 1
            cursor.execute("""UPDATE processed_skus SET status = ?, image_source = ?, image_url = ?,
                           relevance_score = ?, processed_at = ?, attempts = ?, last_error = ? WHERE sku_id = ?""",
                         (status.value, image_source.value if image_source else None, image_url,
                          relevance_score, datetime.utcnow(), attempts, error, sku_id))
        else:
            cursor.execute("""INSERT INTO processed_skus 
                           (sku_id, status, image_source, image_url, relevance_score, last_error)
                           VALUES (?, ?, ?, ?, ?, ?)""",
                         (sku_id, status.value, image_source.value if image_source else None,
                          image_url, relevance_score, error))

        conn.commit()
        conn.close()
        log_msg = f"Marked SKU {sku_id} as {status.value}"
        if image_source:
            log_msg += f" (source: {image_source.value})"
        self.logger.info(log_msg)

    def get_processing_record(self, sku_id: str) -> Optional[ProcessingRecord]:
        """Get processing record for SKU."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM processed_skus WHERE sku_id = ?", (sku_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return ProcessingRecord(
                id=row["id"], sku_id=row["sku_id"], status=ProcessingStatus(row["status"]),
                image_source=ImageSource(row["image_source"]) if row["image_source"] else None,
                image_url=row["image_url"], relevance_score=row["relevance_score"],
                processed_at=datetime.fromisoformat(row["processed_at"]), attempts=row["attempts"],
                last_error=row["last_error"], created_at=datetime.fromisoformat(row["created_at"]))
        return None

    def get_failed_skus(self, retry_limit: int = 3) -> List[str]:
        """Get SKUs that failed but have not exceeded retry limit."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT sku_id FROM processed_skus WHERE status = ? AND attempts < ?",
                      (ProcessingStatus.FAILED.value, retry_limit))
        results = cursor.fetchall()
        conn.close()
        return [row["sku_id"] for row in results]

    def get_needs_review_skus(self) -> List[ProcessingRecord]:
        """Get all SKUs marked as needing manual review."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM processed_skus WHERE status = ? ORDER BY processed_at DESC",
                      (ProcessingStatus.NEEDS_REVIEW.value,))
        results = cursor.fetchall()
        conn.close()

        records = []
        for row in results:
            records.append(ProcessingRecord(
                id=row["id"], sku_id=row["sku_id"], status=ProcessingStatus(row["status"]),
                image_source=ImageSource(row["image_source"]) if row["image_source"] else None,
                image_url=row["image_url"], relevance_score=row["relevance_score"],
                processed_at=datetime.fromisoformat(row["processed_at"]), attempts=row["attempts"],
                last_error=row["last_error"], created_at=datetime.fromisoformat(row["created_at"])))
        return records

    def get_processing_stats(self) -> dict:
        """Get processing statistics."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""SELECT COUNT(*) as total,
                       SUM(CASE WHEN status = ? THEN 1 ELSE 0 END) as successful,
                       SUM(CASE WHEN status = ? THEN 1 ELSE 0 END) as failed,
                       SUM(CASE WHEN status = ? THEN 1 ELSE 0 END) as needs_review
                       FROM processed_skus""",
                      (ProcessingStatus.SUCCESS.value, ProcessingStatus.FAILED.value,
                       ProcessingStatus.NEEDS_REVIEW.value))
        overall = cursor.fetchone()
        cursor.execute("""SELECT image_source, COUNT(*) as count FROM processed_skus
                       WHERE status = ? AND image_source IS NOT NULL GROUP BY image_source""",
                      (ProcessingStatus.SUCCESS.value,))
        source_breakdown = {row["image_source"]: row["count"] for row in cursor.fetchall()}
        conn.close()
        return {"total": overall["total"], "successful": overall["successful"],
                "failed": overall["failed"], "needs_review": overall["needs_review"],
                "source_breakdown": source_breakdown}

    def cleanup_old_records(self, days: int = 30) -> int:
        """Clean up old processing records."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM processed_skus WHERE processed_at < ? AND status = ?",
                      (cutoff_date, ProcessingStatus.SUCCESS.value))
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        self.logger.info(f"Cleaned up {deleted} old records (older than {days} days)")
        return deleted

    def create_execution_record(self, trigger_type: str = "manual") -> int:
        """Create a new execution history record."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO execution_history (trigger_type) VALUES (?)", (trigger_type,))
        execution_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return execution_id

    def update_execution_record(self, execution_id: int, total_skus: int,
                                successful: int, failed: int, skipped: int) -> None:
        """Update execution history record."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT started_at FROM execution_history WHERE id = ?", (execution_id,))
        row = cursor.fetchone()
        if row:
            started_at = datetime.fromisoformat(row["started_at"])
            duration = int((datetime.utcnow() - started_at).total_seconds())
            cursor.execute("""UPDATE execution_history SET completed_at = ?, total_skus = ?,
                           successful = ?, failed = ?, skipped = ?, duration_seconds = ? WHERE id = ?""",
                          (datetime.utcnow(), total_skus, successful, failed, skipped, duration, execution_id))
            conn.commit()
        conn.close()

    def get_last_execution(self) -> Optional[ExecutionHistory]:
        """Get the most recent execution record."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM execution_history ORDER BY started_at DESC LIMIT 1")
        row = cursor.fetchone()
        conn.close()
        if row:
            return ExecutionHistory(
                id=row["id"], started_at=datetime.fromisoformat(row["started_at"]),
                completed_at=datetime.fromisoformat(row["completed_at"]) if row["completed_at"] else None,
                total_skus=row["total_skus"], successful=row["successful"], failed=row["failed"],
                skipped=row["skipped"], duration_seconds=row["duration_seconds"],
                trigger_type=row["trigger_type"])
        return None
