"""
Event ID Generator - Deterministic Event Identification
Generates SHA-256 event_id from source_hash + registry_reference_id.
No randomness. No UUIDs. Fully deterministic and replayable.
"""

import hashlib
from typing import Dict, Any
from datetime import datetime


class EventIDGenerator:
    """
    Generate deterministic event IDs.
    
    Formula: event_id = SHA-256(source_hash + registry_reference_id)
    
    Properties:
    - Same inputs → same event_id (deterministic)
    - No randomness or timestamps
    - Fully replayable
    - Collision resistance (SHA-256)
    """
    
    SEPARATOR = "::"  # Separator between components
    
    @staticmethod
    def generate_event_id(source_hash: str, registry_reference_id: str) -> str:
        """
        Generate deterministic event ID.
        
        Args:
            source_hash: SHA-256 hash of raw content (64 hex chars)
            registry_reference_id: Registry identifier (e.g., "REG_WEATHER_2026_03")
            
        Returns:
            64-character hexadecimal SHA-256 event_id
            
        Raises:
            ValueError: If inputs invalid or empty
        """
        # Validate inputs
        if not source_hash or len(source_hash) != 64:
            raise ValueError("source_hash must be 64-character SHA-256 hex")
        
        if not registry_reference_id:
            raise ValueError("registry_reference_id cannot be empty")
        
        if not isinstance(source_hash, str) or not isinstance(registry_reference_id, str):
            raise ValueError("Both inputs must be strings")
        
        # Combine inputs deterministically
        combined = f"{source_hash}{EventIDGenerator.SEPARATOR}{registry_reference_id}"
        
        # Hash the combination
        event_id_bytes = combined.encode('utf-8')
        event_id_hash = hashlib.sha256(event_id_bytes)
        event_id = event_id_hash.hexdigest()
        
        return event_id
    
    @staticmethod
    def compute_event_id_from_content(raw_content: str, registry_reference_id: str) -> str:
        """
        Generate event ID directly from raw content and registry ID.
        (Convenience function that includes hashing step)
        
        Args:
            raw_content: Raw content from source
            registry_reference_id: Registry ID
            
        Returns:
            Event ID
        """
        # First hash the content
        source_hash = hashlib.sha256(
            raw_content.encode('utf-8')
        ).hexdigest()
        
        # Then generate event ID
        return EventIDGenerator.generate_event_id(source_hash, registry_reference_id)
    
    @staticmethod
    def verify_event_id(source_hash: str, registry_reference_id: str, expected_event_id: str) -> bool:
        """
        Verify that event ID matches inputs.
        
        Args:
            source_hash: Source hash
            registry_reference_id: Registry ID
            expected_event_id: Expected event ID to verify
            
        Returns:
            True if event ID is correct
        """
        computed_id = EventIDGenerator.generate_event_id(source_hash, registry_reference_id)
        return computed_id == expected_event_id


# Singleton instance
_generator = EventIDGenerator()


def generate_event_id(source_hash: str, registry_reference_id: str) -> str:
    """
    Generate deterministic event ID.
    Convenience function.
    
    Args:
        source_hash: SHA-256 hash of raw content
        registry_reference_id: Registry ID
        
    Returns:
        Event ID (64 hex chars)
    """
    return _generator.generate_event_id(source_hash, registry_reference_id)


def compute_event_id_from_content(raw_content: str, registry_reference_id: str) -> str:
    """
    Compute event ID from raw content directly.
    Convenience function.
    
    Args:
        raw_content: Raw content
        registry_reference_id: Registry ID
        
    Returns:
        Event ID
    """
    return _generator.compute_event_id_from_content(raw_content, registry_reference_id)


def verify_event_id(source_hash: str, registry_reference_id: str, expected_event_id: str) -> bool:
    """
    Verify event ID correctness.
    Convenience function.
    
    Args:
        source_hash: Source hash
        registry_reference_id: Registry ID
        expected_event_id: Event ID to verify
        
    Returns:
        True if correct
    """
    return _generator.verify_event_id(source_hash, registry_reference_id, expected_event_id)


def test_event_id_generation():
    """Test event ID generation determinism."""
    print("Testing deterministic event ID generation...")
    
    # Test 1: Determinism - same inputs produce same output
    source_hash = "a" * 64
    registry_id = "REG_WEATHER_2026_03"
    
    event_id_1 = generate_event_id(source_hash, registry_id)
    event_id_2 = generate_event_id(source_hash, registry_id)
    
    deterministic = event_id_1 == event_id_2
    print(f"Determinism test: {'✓ PASS' if deterministic else '✗ FAIL'} - Same inputs → Same event_id")
    print(f"  Event ID: {event_id_1}")
    
    # Test 2: Different registry produces different ID
    event_id_3 = generate_event_id(source_hash, "REG_WEATHER_2026_04")
    different_registry = event_id_1 != event_id_3
    print(f"Sensitivity test (registry): {'✓ PASS' if different_registry else '✗ FAIL'} - Different registry → Different ID")
    
    # Test 3: Different source produces different ID
    event_id_4 = generate_event_id("b" * 64, registry_id)
    different_source = event_id_1 != event_id_4
    print(f"Sensitivity test (source): {'✓ PASS' if different_source else '✗ FAIL'} - Different source → Different ID")
    
    # Test 4: Event ID format
    is_64_hex = len(event_id_1) == 64 and all(c in '0123456789abcdef' for c in event_id_1)
    print(f"Format test: {'✓ PASS' if is_64_hex else '✗ FAIL'} - Event ID is 64-char SHA-256 hex")
    
    # Test 5: Verification works
    verified = verify_event_id(source_hash, registry_id, event_id_1)
    print(f"Verification test: {'✓ PASS' if verified else '✗ FAIL'} - Event ID verification works")
    
    # Test 6: Compute from content
    content = "Test news content for event ID generation"
    event_id_5 = compute_event_id_from_content(content, registry_id)
    event_id_5_repeat = compute_event_id_from_content(content, registry_id)
    
    content_deterministic = event_id_5 == event_id_5_repeat
    print(f"Content-based determinism: {'✓ PASS' if content_deterministic else '✗ FAIL'} - Content → event_id deterministic")


if __name__ == "__main__":
    test_event_id_generation()
