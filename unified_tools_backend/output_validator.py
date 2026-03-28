"""
Output Standardization Validator
Phase 9: Verifies all output records match ingestion_contract_v1.json schema.
Comprehensive validation of all mandatory fields and constraints.
"""

import json
from typing import Dict, Any, List, Tuple
from pathlib import Path


class OutputValidator:
    """
    Validates output records against ingestion contract schema.
    Ensures:
    - All mandatory fields present
    - No extra/unauthorized fields
    - Field types correct
    - Field values satisfy constraints
    - Event IDs are properly formatted (64-char hex SHA-256)
    - Truth levels are valid (0-4)
    - Geo normalized structure is correct
    """
    
    # Mandatory fields defined in ingestion_contract_v1.json
    MANDATORY_FIELDS = {
        "event_id": "string",
        "source_url": "string",
        "source_hash": "string",
        "ingestion_timestamp": "string",
        "raw_content": "string",
        "truth_level": "integer",
        "conflict_flag": "boolean",
        "registry_reference_id": "string",
        "geo_normalized": ["object", "null"]
    }
    
    VALID_TRUTH_LEVELS = [0, 1, 2, 3, 4]
    
    GEO_NORMALIZED_FIELDS = {
        "country_code": "string",
        "region": ["string", "null"],
        "latitude": ["number", "null"],
        "longitude": ["number", "null"],
        "confidence": ["number", "null"]
    }
    
    def __init__(self):
        """Initialize validator."""
        self.validation_results = []
        self.total_records = 0
        self.valid_records = 0
        self.invalid_records = 0
        self.validation_errors = []
    
    def validate_record(self, record: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate a single record against output schema.
        
        Args:
            record: Record to validate
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        self.total_records += 1
        errors = []
        
        # 1. Check all mandatory fields present
        for field_name, field_type in self.MANDATORY_FIELDS.items():
            if field_name not in record:
                errors.append(f"Missing mandatory field: {field_name}")
            else:
                # 2. Check field type
                field_value = record[field_name]
                if isinstance(field_type, list):
                    # Allow multiple types (e.g., "string" or "null")
                    if not any(self._check_type(field_value, t) for t in field_type):
                        errors.append(
                            f"Field {field_name} has wrong type. "
                            f"Expected one of {field_type}, got {type(field_value).__name__}"
                        )
                else:
                    if not self._check_type(field_value, field_type):
                        errors.append(
                            f"Field {field_name} has wrong type. "
                            f"Expected {field_type}, got {type(field_value).__name__}"
                        )
                
                # 3. Validate specific field constraints
                if field_name == "event_id":
                    if not self._validate_event_id(field_value):
                        errors.append(
                            f"event_id format invalid: must be 64-char hex SHA-256, got {field_value}"
                        )
                
                elif field_name == "truth_level":
                    if field_value not in self.VALID_TRUTH_LEVELS:
                        errors.append(
                            f"truth_level invalid: must be one of {self.VALID_TRUTH_LEVELS}, got {field_value}"
                        )
                
                elif field_name == "geo_normalized":
                    if field_value is not None:
                        geo_errors = self._validate_geo_normalized(field_value)
                        errors.extend(geo_errors)
                
                elif field_name == "conflict_flag":
                    if not isinstance(field_value, bool):
                        errors.append(
                            f"conflict_flag must be boolean, got {type(field_value).__name__}"
                        )
                
                elif field_name in ["source_url", "source_hash", "ingestion_timestamp", 
                                   "raw_content", "registry_reference_id"]:
                    if not isinstance(field_value, str):
                        errors.append(
                            f"{field_name} must be string, got {type(field_value).__name__}"
                        )
                    if isinstance(field_value, str) and len(field_value) == 0:
                        errors.append(f"{field_name} cannot be empty string")
        
        # 4. Check for unexpected fields
        unexpected_fields = set(record.keys()) - set(self.MANDATORY_FIELDS.keys())
        for field_name in unexpected_fields:
            errors.append(f"Unexpected field: {field_name} (not in contract)")
        
        # Update statistics
        is_valid = len(errors) == 0
        if is_valid:
            self.valid_records += 1
        else:
            self.invalid_records += 1
            self.validation_errors.extend(errors)
        
        self.validation_results.append({
            "record": record,
            "is_valid": is_valid,
            "errors": errors
        })
        
        return is_valid, errors
    
    def validate_batch(self, records: List[Dict[str, Any]]) -> Tuple[int, int, List[Dict[str, Any]]]:
        """
        Validate a batch of records.
        
        Args:
            records: List of records to validate
            
        Returns:
            Tuple of (valid_count, invalid_count, validation_results)
        """
        results = []
        valid_count = 0
        invalid_count = 0
        
        for record in records:
            is_valid, errors = self.validate_record(record)
            results.append({
                "record_id": record.get("event_id", "unknown"),
                "is_valid": is_valid,
                "error_count": len(errors),
                "errors": errors
            })
            if is_valid:
                valid_count += 1
            else:
                invalid_count += 1
        
        return valid_count, invalid_count, results
    
    def _check_type(self, value: Any, type_name: str) -> bool:
        """Check if value matches type."""
        type_map = {
            "string": str,
            "integer": int,
            "number": (int, float),
            "boolean": bool,
            "object": dict,
            "null": type(None),
            "array": list
        }
        expected_type = type_map.get(type_name)
        if expected_type is None:
            return False
        return isinstance(value, expected_type)
    
    def _validate_event_id(self, event_id: str) -> bool:
        """Validate event ID format (64-char hex SHA-256)."""
        if not isinstance(event_id, str):
            return False
        if len(event_id) != 64:
            return False
        try:
            int(event_id, 16)  # Must be valid hex
            return True
        except ValueError:
            return False
    
    def _validate_geo_normalized(self, geo_obj: Dict[str, Any]) -> List[str]:
        """Validate geo_normalized object structure."""
        errors = []
        
        if not isinstance(geo_obj, dict):
            errors.append("geo_normalized must be object or null")
            return errors
        
        # Check mandatory geo fields
        if "country_code" not in geo_obj:
            errors.append("geo_normalized: missing mandatory field country_code")
        else:
            country_code = geo_obj["country_code"]
            if not isinstance(country_code, str):
                errors.append(
                    f"geo_normalized.country_code must be string, got {type(country_code).__name__}"
                )
            elif len(country_code) != 2:
                errors.append(
                    f"geo_normalized.country_code must be 2-char code, got {country_code}"
                )
        
        # Check optional geo fields
        for field_name, field_types in self.GEO_NORMALIZED_FIELDS.items():
            if field_name == "country_code":
                continue  # Already checked above
            
            if field_name in geo_obj:
                field_value = geo_obj[field_name]
                if not any(self._check_type(field_value, t) for t in field_types):
                    errors.append(
                        f"geo_normalized.{field_name} has wrong type. "
                        f"Expected one of {field_types}, got {type(field_value).__name__}"
                    )
                
                # Validate field constraints
                if field_name == "latitude":
                    if field_value is not None and (field_value < -90 or field_value > 90):
                        errors.append(f"geo_normalized.latitude out of range: {field_value}")
                
                elif field_name == "longitude":
                    if field_value is not None and (field_value < -180 or field_value > 180):
                        errors.append(f"geo_normalized.longitude out of range: {field_value}")
                
                elif field_name == "confidence":
                    if field_value is not None and (field_value < 0 or field_value > 1):
                        errors.append(f"geo_normalized.confidence out of range: {field_value}")
        
        return errors
    
    def get_validation_report(self) -> Dict[str, Any]:
        """Get overall validation report."""
        return {
            "validation_report": {
                "total_records": self.total_records,
                "valid_records": self.valid_records,
                "invalid_records": self.invalid_records,
                "validity_rate": (self.valid_records / self.total_records * 100) if self.total_records > 0 else 0,
                "validation_summary": {
                    "all_records_valid": self.invalid_records == 0,
                    "error_count": len(self.validation_errors),
                    "unique_errors": list(set(self.validation_errors))
                }
            }
        }
    
    def get_detailed_results(self) -> List[Dict[str, Any]]:
        """Get detailed validation results."""
        return self.validation_results


def test_output_validator():
    """Test output validation."""
    print("Testing output validator...")
    
    validator = OutputValidator()
    
    # Test valid record
    valid_record = {
        "event_id": "a" * 64,
        "source_url": "https://example.com/news",
        "source_hash": "b" * 64,
        "ingestion_timestamp": "2026-03-15T10:30:00Z",
        "raw_content": "Test content",
        "truth_level": 3,
        "conflict_flag": False,
        "registry_reference_id": "REG_TEST_001",
        "geo_normalized": {
            "country_code": "IN",
            "region": "Maharashtra",
            "latitude": 19.0760,
            "longitude": 72.8777,
            "confidence": 0.95
        }
    }
    
    is_valid, errors = validator.validate_record(valid_record)
    print(f"Valid Record: {is_valid}")
    if errors:
        print(f"  Errors: {errors}")
    
    # Test invalid record (missing field)
    invalid_record = {
        "event_id": "a" * 64,
        "source_url": "https://example.com/news",
        # Missing source_hash
        "ingestion_timestamp": "2026-03-15T10:30:00Z",
        "raw_content": "Test content",
        "truth_level": 3,
        "conflict_flag": False,
        "registry_reference_id": "REG_TEST_001",
        "geo_normalized": None
    }
    
    is_valid2, errors2 = validator.validate_record(invalid_record)
    print(f"\nInvalid Record (missing field): {is_valid2}")
    if errors2:
        print(f"  Errors: {errors2}")
    
    # Test invalid record (bad truth_level)
    bad_truth_record = {
        "event_id": "a" * 64,
        "source_url": "https://example.com/news",
        "source_hash": "b" * 64,
        "ingestion_timestamp": "2026-03-15T10:30:00Z",
        "raw_content": "Test content",
        "truth_level": 5,  # Invalid - must be 0-4
        "conflict_flag": False,
        "registry_reference_id": "REG_TEST_001",
        "geo_normalized": None
    }
    
    is_valid3, errors3 = validator.validate_record(bad_truth_record)
    print(f"\nInvalid Record (bad truth_level): {is_valid3}")
    if errors3:
        print(f"  Errors: {errors3}")
    
    # Get final report
    report = validator.get_validation_report()
    print(f"\n{json.dumps(report, indent=2)}")


if __name__ == "__main__":
    test_output_validator()
