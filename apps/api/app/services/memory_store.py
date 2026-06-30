import os
import re
from sqlalchemy.orm import Session
from app.models.memory import FixPatternMemory

class MemoryStoreService:

    @staticmethod
    def _extract_error_type(tool: str, message: str) -> str:
        """
        Helper to extract error codes like F821, B101, etc., from message strings.
        """
        # Search for code in brackets or prefix
        code_match = re.search(r'\[([A-Z0-9_-]+)\]', message)
        if code_match:
            return code_match.group(1)
        
        # Search for typical rule patterns (e.g. F821, B101)
        pattern_match = re.search(r'\b([A-Z]\d{3})\b', message)
        if pattern_match:
            return pattern_match.group(1)
            
        # Fallback to first word or generic
        words = message.split()
        return words[0] if words else "generic"

    @staticmethod
    def get_relevant_patch(
        db: Session,
        tool: str,
        message: str,
        file_path: str
    ) -> str | None:
        """
        Queries the database for a similar successful fix pattern.
        """
        if not db:
            return None
            
        ext = os.path.splitext(file_path)[-1].lower()
        error_type = MemoryStoreService._extract_error_type(tool, message)
        
        # Search for matching tool, error_type, and file extension
        match = db.query(FixPatternMemory).filter(
            FixPatternMemory.tool == tool,
            FixPatternMemory.error_type == error_type,
            FixPatternMemory.file_extension == ext
        ).first()
        
        if match:
            print(f"Memory Hit! Found previous successful patch for {tool} [{error_type}].")
            return match.successful_patch  # type: ignore
            
        return None

    @staticmethod
    def save_fix_pattern(
        db: Session,
        tool: str,
        message: str,
        file_path: str,
        successful_patch: str
    ):
        """
        Saves a successful fix pattern to the DB for future runs.
        """
        if not db or not successful_patch:
            return
            
        ext = os.path.splitext(file_path)[-1].lower()
        error_type = MemoryStoreService._extract_error_type(tool, message)
        
        # Avoid duplicate memories
        exists = db.query(FixPatternMemory).filter(
            FixPatternMemory.tool == tool,
            FixPatternMemory.error_type == error_type,
            FixPatternMemory.file_extension == ext,
            FixPatternMemory.successful_patch == successful_patch
        ).first()
        
        if not exists:
            try:
                memory = FixPatternMemory(
                    tool=tool,
                    error_type=error_type,
                    file_extension=ext,
                    error_context=message,
                    successful_patch=successful_patch
                )
                db.add(memory)
                db.commit()
                print(f"Successfully recorded successful fix pattern into memory: {tool} [{error_type}]")
            except Exception as e:
                db.rollback()
                print(f"Failed to save fix pattern memory to DB: {e}")
