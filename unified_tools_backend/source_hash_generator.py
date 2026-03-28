"""
Source Hash Generator - Pre-Parse Deterministic Hashing
Generates SHA-256 hashes of raw content BEFORE parsing.
Same source → same hash. Always. Deterministic.
"""

import hashlib
from typing import Dict, Any
from datetime import datetime


class SourceHashGenerator:
    """
    Generate source hashes BEFORE any content parsing.
    
    Ensures:
    - Deterministic identification of sources
    - Same raw content always produces same hash
    - Hash is generated pre-parse (no parsing side effects)
    - Replayable and auditable
    """
    
    @staticmethod
    def generate_source_hash(raw_content: str) -> str:
        """
        Generate SHA-256 hash of raw content.
        
        Args:
            raw_content: Raw, unprocessed content from source
            
        Returns:
            64-character hexadecimal SHA-256 hash
            
        Raises:
            ValueError: If content is empty or invalid
        """
        if not raw_content:
            raise ValueError("raw_content cannot be empty")
        
        if not isinstance(raw_content, str):
            raise ValueError("raw_content must be string")
        
        # Normalize: encode to UTF-8, hash
        content_bytes = raw_content.encode('utf-8')
        hash_obj = hashlib.sha256(content_bytes)
        hash_hex = hash_obj.hexdigest()
        
        return hash_hex
    
    @staticmethod
    def verify_source_hash(raw_content: str, expected_hash: str) -> bool:
        """
        Verify that raw content matches expected hash.
        
        Args:
            raw_content: Raw content to verify
            expected_hash: Expected SHA-256 hash
            
        Returns:
            True if hash matches, False otherwise
        """
        computed_hash = SourceHashGenerator.generate_source_hash(raw_content)
        return computed_hash == expected_hash
    
    @staticmethod
    def get_source_metadata(source_url: str, raw_content: str) -> Dict[str, Any]:
        """
        Get complete source metadata including hash.
        
        Args:
            source_url: Source URL
            raw_content: Raw content
            
        Returns:
            Dictionary with source metadata
        """
        source_hash = SourceHashGenerator.generate_source_hash(raw_content)
        
        return {
            "source_url": source_url,
            "source_hash": source_hash,
            "content_length": len(raw_content),
            "hash_algorithm": "SHA-256",
            "generated_at": datetime.utcnow().isoformat()
        }


# Singleton instance
_generator = SourceHashGenerator()


def generate_source_hash(raw_content: str) -> str:
    """
    Generate SHA-256 hash of raw content.
    Convenience function.
    
    Args:
        raw_content: Raw content
        
    Returns:
        SHA-256 hash (64 hex characters)
    """
    return _generator.generate_source_hash(raw_content)


def verify_source_hash(raw_content: str, expected_hash: str) -> bool:
    """
    Verify source hash matches content.
    Convenience function.
    
    Args:
        raw_content: Raw content
        expected_hash: Expected hash
        
    Returns:
        True if matches
    """
    return _generator.verify_source_hash(raw_content, expected_hash)


def get_source_metadata(source_url: str, raw_content: str) -> Dict[str, Any]:
    """
    Get source metadata including hash.
    Convenience function.
    
    Args:
        source_url: Source URL
        raw_content: Raw content
        
    Returns:
        Metadata dictionary
    """
    return _generator.get_source_metadata(source_url, raw_content)


def test_hash_generation():
    """Test hash generation determinism."""
    print("Testing source hash generation...")
    
    # Test 1: Same content produces same hash
    content1 = "This is test news content"
    hash1 = generate_source_hash(content1)
    hash2 = generate_source_hash(content1)
    
    match = hash1 == hash2
    print(f"Determinism test: {'✓ PASS' if match else '✗ FAIL'} - Same content → Same hash")
    print(f"  Hash: {hash1}")
    
    # Test 2: Different content produces different hash
    content2 = "This is different content"
    hash3 = generate_source_hash(content2)
    
    different = hash1 != hash3
    print(f"Uniqueness test: {'✓ PASS' if different else '✗ FAIL'} - Different content → Different hash")
    
    # Test 3: Hash verification
    is_valid = verify_source_hash(content1, hash1)
    print(f"Verification test: {'✓ PASS' if is_valid else '✗ FAIL'} - Content matches hash")
    
    # Test 4: Hash format
    is_64_hex = len(hash1) == 64 and all(c in '0123456789abcdef' for c in hash1)
    print(f"Format test: {'✓ PASS' if is_64_hex else '✗ FAIL'} - Hash is 64-char hex")
    
    # Test 5: Metadata generation
    metadata = get_source_metadata("https://example.com", content1)
    has_hash = "source_hash" in metadata and metadata["source_hash"] == hash1
    print(f"Metadata test: {'✓ PASS' if has_hash else '✗ FAIL'} - Metadata includes correct hash")


if __name__ == "__main__":
    test_hash_generation()
