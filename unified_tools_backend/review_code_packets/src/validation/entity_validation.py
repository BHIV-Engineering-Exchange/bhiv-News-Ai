import re
from analysis.entity_filters import (ENTITY_REJECTION_RULES, GENERIC_ENTITY_TERMS)
from analysis.entity_patterns import (OCR_PATTERNS,FILE_PATTERNS,TECHNICAL_PATTERNS,DOCUMENT_PATTERNS,
        BUSINESS_INTELLIGENCE_TERMS, DOCUMENT_HEADING_PATTERNS,SOFTWARE_TERMS,FRAMEWORK_TERMS,DATABASE_TERMS,
        HTTP_TERMS,SQL_TERMS,TECHNICAL_SUFFIXES,TECHNICAL_PHRASES)

class EntityValidator:
    """
    Validates extracted entities.

    Responsibilities:
    - Remove false positives
    - Explain every rejection
    - Normalize entities
    - Produce validated and rejected entity reports
    """

    ENTITY_TYPE_MAPPING = {
        "names": "PERSON",
        "organizations": "ORG",
        "locations": "GPE"
    }

    def validate(self, entities: dict) -> dict:
        validated_entities = {}
        rejected_entities = []

        for entity_group, values in entities.items():
            validated_entities[entity_group] = []
            ner_type = self.ENTITY_TYPE_MAPPING.get(entity_group)

            for value in values:
                is_valid, reason = self._validate_entity(value,ner_type,entity_group)

                if is_valid:
                    # Normalize organizations
                    if entity_group == "organizations":
                        value = self._normalize_org_name(value)

                    validated_entities[entity_group].append(value)

                else:
                    rejected_entities.append({
                        "entity": value,
                        "entity_type":
                            ner_type
                            if ner_type
                            else entity_group,
                        "reason": reason
                    })

        # Remove duplicate person names
        if "names" in validated_entities:
            validated_entities["names"] = (
                self._remove_duplicate_person_names(
                    validated_entities["names"]
                )
            )

        # Remove duplicate organizations
        if "organizations" in validated_entities:
            validated_entities["organizations"] = sorted(
                list(set(validated_entities["organizations"]))
            )

        # -------------------------------------------------------
        # Remove organizations that are part of detected persons
        # -------------------------------------------------------

        if ("names" in validated_entities
            and "organizations" in validated_entities
        ):
            validated_names = set(validated_entities["names"])
            clean_organizations = []

            for org in validated_entities["organizations"]:
                # Single-word organizations only
                if len(org.split()) == 1:
                    if any(org.lower() in [part.lower() for part in person.split()]
                            for person in validated_names
                        ):
                        rejected_entities.append({
                            "entity": org,
                            "entity_type": "ORG",
                            "reason": "Appears inside detected person name"
                        })

                        continue

                clean_organizations.append(org)
            validated_entities["organizations"] = clean_organizations

        # -------------------------------------------------------
        # Remove locations that are part of detected persons
        # -------------------------------------------------------

        if ("names" in validated_entities
            and "locations" in validated_entities
        ):
            validated_names = set(validated_entities["names"])
            clean_locations = []

            for location in validated_entities["locations"]:
                if any(location.lower() in [part.lower() for part in person.split()]
                    for person in validated_names
                ):
                    rejected_entities.append({
                        "entity": location,
                        "entity_type": "GPE",
                        "reason": "Appears inside detected person name"
                    })

                    continue

                clean_locations.append(location)
            validated_entities["locations"] = clean_locations

        return {
            "validated_entities": validated_entities,
            "rejected_entities": rejected_entities
        }

    def _validate_entity(self,entity: str,entity_type: str | None,entity_group: str):
        candidate = entity.strip()

        # Preserve Valid Emails
        if entity_group == "emails":
            return (True, "Valid email")

        # Preserve Valid Phones
        if entity_group == "phone_numbers":
            return (True, "Valid phone number")

        if not candidate:
            return (False,"Empty entity")

        if len(candidate) < 2:
            return (False, "Entity too short")

        # Handle years
        if candidate.isdigit():
            if (
                entity_group == "dates"
                and len(candidate) == 4
                and 1900 <= int(candidate) <= 2100
            ):
                return (True, "Valid year")

            return (False, "Numeric token")

        normalized = (candidate.lower().strip())

        if entity_type == "emails":
            return (True, "Valid email")
        
        # File Name Detection
        for pattern in FILE_PATTERNS:
            if re.fullmatch(pattern, normalized):
                return ( False, "File reference detected")

        
        # Document Structure
        if normalized in DOCUMENT_PATTERNS:
            return (False, "Document structure term")
        
        if normalized in BUSINESS_INTELLIGENCE_TERMS:
            return( False, "Business Intelligence terms")

        # Technical Concepts
        for pattern in TECHNICAL_PATTERNS:
            if re.fullmatch(pattern, normalized):

                return (False, "Technical concept")

        # Generic terms
        if normalized in GENERIC_ENTITY_TERMS:
            return (False, "Generic operational term")

        # Document reference number
        if re.fullmatch(r"\d{1,5}-\d{1,5}", candidate):
            return (False,"Document reference number")

        # Invalid punctuation
        if re.search(
            r"[-_]{2,}",
            candidate
        ):
            return (False,"Contains invalid punctuation pattern")

        # Mostly punctuation
        alpha_count = sum(
            char.isalpha()
            for char in candidate
        )

        # Explainable blacklist
        if entity_type:
            rejection_rules = (ENTITY_REJECTION_RULES.get(entity_type, {}))

            if normalized in rejection_rules:
                return (False,rejection_rules[normalized])

        # PERSON validation
        if entity_type == "PERSON":
            words = candidate.split()
            invalid_person_terms = {
                "distribution","input","output","life","remaining",
                "intelligence"
            }
            for word in words:
                if word.lower() in invalid_person_terms:

                    return (
                        False,
                        "Technical phrase, not a person"
                    )
            
# ------>   
# 
            if len(words) == 1:
                if len(candidate) < 5:
                    return (False, "Suspicious short single-token name")
                
            if len(words) > 5:
                return (False, "Heading-like entity")
            
            if "-" in candidate:
                return (False, "Hyphenated technical phrase")

            if len(words) == 1:
                # Reject obvious non-persons
                if not candidate[0].isupper():
                    return (False, "Improper capitalization")

                if len(candidate) < 3:
                    return (False,"Name too short")

                return (True,"Valid single-token name")

            if candidate.islower():
                return (False, "Improper capitalization")

            if not all(
                word[0].isupper()
                for word in words
                if word
            ):

                return (False, "Invalid name structure")

        # Reject file extensions

        if "." in normalized:
            if normalized.endswith((".app",".exe",".js",".ts",".py",".java")):
                return (False,"Software file/application")  
            
        # ORG validation
        #3
        if entity_type == "ORG":
            for pattern in DOCUMENT_HEADING_PATTERNS:
                if re.search(pattern, normalized):
                    return (False,"Document heading")

            if ":" in candidate:
                return (False,"Document heading")

            uppercase_ratio = (
                sum(char.isupper() for char in candidate)
                / max(len(candidate), 1)
            )

            if (
                uppercase_ratio > 0.35
                and len(candidate.split()) >= 2
            ):

                return (False,"Likely document heading")

            if candidate.islower():
                return (False,"Improper organization capitalization")

            # Technical software
            if normalized in SOFTWARE_TERMS:
                return (False,"Software application")
            
            # Frameworks
            if normalized in FRAMEWORK_TERMS:
                return (False,"Software framework")

            # Databases
            if normalized in DATABASE_TERMS:
                return (False,"Database technology")

            # HTTP methods
            if normalized in HTTP_TERMS:
                return (False,"HTTP method")

            # SQL keywords
            if normalized in SQL_TERMS:
                return (False,"SQL keyword")

            # Technical suffix
            for suffix in TECHNICAL_SUFFIXES:
                if normalized.endswith(suffix):
                    return (False,"Technical component")

            for phrase in TECHNICAL_PHRASES:
                if phrase in normalized:
                    return (False,"Technical project phrase")
                
            words = candidate.split()
            # if (
            #     len(words) in [2, 3]
            #     and all(
            #         word[0].isupper()
            #         for word in words
            #         if word
            #     )
            # ):
            #     return (False,"Likely person name misclassified as organization")

            # ---------------------------------------------
            # Extremely long ORG names are usually headings
            # ---------------------------------------------

            if len(words) > 8:
                return (False,"Unusually long organization name")
            
        # GPE validation
        if entity_type == "GPE":
            invalid_location_terms = {
                "emission","emissions","gas","gases","pollution","carbon","CSS3"
            }

            if normalized in invalid_location_terms:
                return (False,"Environmental term, not a location")
        
        technical_person_patterns = [
            r".*based.*",r".*developed.*",r".*system.*",r".*model.*",
            r".*framework.*",r".*application.*",r".*chatbot.*"
            ]

        for pattern in technical_person_patterns:
            if re.fullmatch(pattern, normalized):
                return (False, "Technical phrase, not a person")
            
        return (True, "Valid entity")

    def _remove_duplicate_person_names(self,names: list):
        full_names = {
            name
            for name in names
            if len(name.split()) > 1
        }

        filtered = []
        for name in names:
            if len(name.split()) == 1:
                exists_in_full_name = any(
                    name in full.split()
                    for full in full_names
                )

                if exists_in_full_name:
                    continue

            filtered.append(name)

        return sorted(list(set(filtered)))
    
    def _normalize_org_name(self,org: str):
        normalized = org.strip()

        if normalized.lower().startswith("the "):
            normalized = normalized[4:]

        return normalized