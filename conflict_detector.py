"""
Conflict Detector Module
Detects structural contradictions based on registry_reference_id.
"""

from typing import List, Dict, Any

def detect_conflicts(registry_id: str, new_entry: Dict[str, Any], existing_entries: List[Dict[str, Any]]) -> bool:
    """
    Detects structural contradictions between a new entry and existing entries
    associated with the same registry_reference_id.
    """
    for existing in existing_entries:
        if existing.get('registry_reference_id') != registry_id:
            continue
            
        # 1. Check for conflicting numeric values
        # Example: 'population' or 'count' fields
        numeric_fields = ['population', 'count', 'amount', 'price']
        for field in numeric_fields:
            if field in new_entry and field in existing:
                if new_entry[field] != existing[field]:
                    return True

        # 2. Check for opposing categorical claims
        # Example: 'status', 'outcome', 'type'
        categorical_fields = ['status', 'outcome', 'type', 'state']
        for field in categorical_fields:
            if field in new_entry and field in existing:
                if new_entry[field] != existing[field]:
                    return True

        # 3. Check for incompatible event states
        # Example: 'is_active', 'is_complete'
        boolean_fields = ['is_active', 'is_complete', 'verified']
        for field in boolean_fields:
            if field in new_entry and field in existing:
                if new_entry[field] != existing[field]:
                    return True

    return False
