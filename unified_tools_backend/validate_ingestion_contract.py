"""
Schema Validator for Truth Intelligence Ingestion Contract v1
Validates every incoming record against the canonical schema.
No exceptions. No shortcuts. Strict determinism.
"""

import json
import os
from typing import Dict, Any, Tuple, List
from pathlib import Path
import jsonschema
from datetime import datetime

# Load the canonical schema
SCHEMA_PATH = os.path.join(
    os.path.dirname(__file__),
    "..",
    "ingestion_contract_v1.json"
)


def load_schema() -> Dict[str, Any]:
    """Load canonical ingestion schema."""
    with open(SCHEMA_PATH, 'r') as f:
        return json.load(f)


class ValidationError(Exception):
    """Raised when record validation fails."""
    pass


class IngestionContractValidator:
    """
    Strict schema validator for ingestion pipeline.
    
    Validates:
    - All mandatory fields present
    - Field types correct
    - Field ranges valid
    - No extra fields allowed
    - Deterministic output
    """
    
    def __init__(self):
        """Initialize validator with canonical schema."""
        self.schema = load_schema()
        self.validation_errors: List[Dict[str, Any]] = []
        self.validation_success: List[Dict[str, Any]] = []
        
    def validate_record(self, record: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate a single ingestion record.
        
        Args:
            record: Record to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Use jsonschema to validate
            jsonschema.validate(instance=record, schema=self.schema)
            
            # Additional deterministic checks
            self._check_determinism(record)
            
            # Log success
            self.validation_success.append({
                "event_id": record.get("event_id"),
                "timestamp": datetime.utcnow().isoformat(),
                "status": "VALID"
            })
            
            return True, ""
            
        except jsonschema.ValidationError as e:
            error_msg = f"Schema validation failed: {e.message} at {'.'.join(str(x) for x in e.absolute_path)}"
            self._log_error(record, error_msg)
            return False, error_msg
            
        except ValueError as e:
            error_msg = f"Determinism check failed: {str(e)}"
            self._log_error(record, error_msg)
            return False, error_msg
            
        except Exception as e:
            error_msg = f"Unexpected validation error: {str(e)}"
            self._log_error(record, error_msg)
            return False, error_msg
    
    def _check_determinism(self, record: Dict[str, Any]) -> None:
        """
        Check deterministic constraints beyond schema.
        
        Args:
            record: Record to check
            
        Raises:
            ValueError: If determinism violated
        """
        # Check required string lengths are not empty
        if not record.get("event_id") or len(record["event_id"]) != 64:
            raise ValueError("event_id must be 64-char SHA-256 hash")
        
        if not record.get("source_hash") or len(record["source_hash"]) != 64:
            raise ValueError("source_hash must be 64-char SHA-256 hash")
        
        # Check truth_level is one of allowed values
        if record.get("truth_level") not in [0, 1, 2, 3, 4]:
            raise ValueError(f"truth_level must be 0-4, got {record.get('truth_level')}")
        
        # Check conflict_flag is boolean
        if not isinstance(record.get("conflict_flag"), bool):
            raise ValueError("conflict_flag must be boolean")
        
        # Check geo_normalized is either object or null
        geo = record.get("geo_normalized")
        if geo is not None and not isinstance(geo, dict):
            raise ValueError("geo_normalized must be object or null")
        
        # Check timestamp is valid ISO 8601
        try:
            datetime.fromisoformat(record.get("ingestion_timestamp", "").replace('Z', '+00:00'))
        except (ValueError, TypeError):
            raise ValueError("ingestion_timestamp must be valid ISO 8601")
    
    def _log_error(self, record: Dict[str, Any], error_msg: str) -> None:
        """Log validation error."""
        self.validation_errors.append({
            "event_id": record.get("event_id", "UNKNOWN"),
            "timestamp": datetime.utcnow().isoformat(),
            "status": "INVALID",
            "error": error_msg
        })
    
    def validate_batch(self, records: List[Dict[str, Any]]) -> Tuple[int, int, List[Dict]]:
        """
        Validate a batch of records.
        
        Args:
            records: List of records to validate
            
        Returns:
            Tuple of (valid_count, invalid_count, invalid_records)
        """
        invalid_records = []
        
        for record in records:
            is_valid, error_msg = self.validate_record(record)
            if not is_valid:
                invalid_records.append({
                    "record": record,
                    "error": error_msg
                })
        
        valid_count = len(records) - len(invalid_records)
        invalid_count = len(invalid_records)
        
        return valid_count, invalid_count, invalid_records
    
    def get_validation_report(self) -> Dict[str, Any]:
        """Get comprehensive validation report."""
        return {
            "total_valid": len(self.validation_success),
            "total_invalid": len(self.validation_errors),
            "success_records": self.validation_success,
            "error_records": self.validation_errors,
            "report_timestamp": datetime.utcnow().isoformat()
        }
    
    def reset(self) -> None:
        """Reset validation logs."""
        self.validation_errors = []
        self.validation_success = []


# Singleton instance
_validator = None


def get_validator() -> IngestionContractValidator:
    """Get or create global validator instance."""
    global _validator
    if _validator is None:
        _validator = IngestionContractValidator()
    return _validator


def validate_ingestion_record(record: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Validate a single ingestion record.
    
    Args:
        record: Record to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    validator = get_validator()
    return validator.validate_record(record)


def validate_ingestion_batch(records: List[Dict[str, Any]]) -> Tuple[int, int, List[Dict]]:
    """
    Validate a batch of ingestion records.
    
    Args:
        records: List of records
        
    Returns:
        Tuple of (valid_count, invalid_count, invalid_records)
    """
    validator = get_validator()
    return validator.validate_batch(records)


def get_validation_report() -> Dict[str, Any]:
    """Get validation report."""
    validator = get_validator()
    return validator.get_validation_report()


# Test helper
def test_schema_validation():
    """Test schema validation."""
    print("Testing ingestion contract schema validation...")
    
    # Valid record
    valid_record = {
        "event_id": "a" * 64,
        "source_url": "https://example.com/news",
        "source_hash": "b" * 64,
        "ingestion_timestamp": "2026-03-28T12:00:00Z",
        "raw_content": "Example news content",
        "truth_level": 3,
        "conflict_flag": False,
        "registry_reference_id": "REG_NEWS_2026",
        "geo_normalized": None
    }
    
    validator = get_validator()
    is_valid, error = validator.validate_record(valid_record)
    print(f"Valid record test: {'✓ PASS' if is_valid else '✗ FAIL'} - {error}")
    
    # Missing required field
    invalid_record = valid_record.copy()
    del invalid_record["event_id"]
    is_valid, error = validator.validate_record(invalid_record)
    print(f"Missing field test: {'✓ PASS' if not is_valid else '✗ FAIL'} - {error[:50]}")
    
    # Invalid truth_level
    invalid_record = valid_record.copy()
    invalid_record["truth_level"] = 10
    is_valid, error = validator.validate_record(invalid_record)
    print(f"Invalid truth_level test: {'✓ PASS' if not is_valid else '✗ FAIL'} - {error[:50]}")


if __name__ == "__main__":
    test_schema_validation()
