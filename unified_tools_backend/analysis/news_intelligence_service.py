from datetime import datetime
import re

from analysis.entity_extractor import EntityExtractor
from validation.entity_validator import EntityValidator
from analysis.classification_engine import ClassificationEngine
from analysis.evidence_engine import EvidenceEngine
from analysis.confidence_engine import ConfidenceEngine


class NewsIntelligenceService:
    """
    Bridge between News-AI and Intake Intelligence Engine.

    Performs:
    - Entity Extraction
    - Entity Validation
    - News Classification
    - Evidence Generation
    - Confidence Calculation
    - Processing Trace
    """

    def __init__(self):
        self.extractor = EntityExtractor()
        self.validator = EntityValidator()
        self.classifier = ClassificationEngine()
        self.evidence_engine = EvidenceEngine()
        self.confidence_engine = ConfidenceEngine()

    def process(self, scraped_data: dict, scraping_time: float = 0):

        processing_times = {}

        title = scraped_data.get("title", "")
        content = scraped_data.get("content", "")
        publication_date = scraped_data.get("publication_date", "")

        # Extract clean publication date
        date_match = re.search(
            r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},\s+\d{4}",
            publication_date,
            re.IGNORECASE,
        )

        clean_publication_date = (
            date_match.group(0)
            if date_match
            else ""
        )

        
        # Build clean document
        document = f"""
Title:
{title}

Published:
{clean_publication_date}

Content:
{content}
"""

        # Normalize possessive names
        document = re.sub(r"[’']s\b", "", document)

        # Remove scraper noise
        SCRAPER_NOISE = [
            "Advertisement","Advertisements","Loading","Recommendations","Recommended","Read More","Follow Us",
            "Share","WhatsApp","Telegram","Click Here","Subscribe","Sign In","Sign Up","Log In","Log Out","Login",
            "Logout","Register","Search","Search Now",
        ]

        for noise in SCRAPER_NOISE:
            document = document.replace(noise, "")

        # Entity Extraction
        start = datetime.now()

        extracted_entities = self.extractor.extract(document)

        processing_times["entity_extraction"] = round(
            (datetime.now() - start).total_seconds(),
            2
        )

        # Validation
        start = datetime.now()
        validated_entities = self.validator.validate(extracted_entities)

        processing_times["validation"] = round(
            (datetime.now() - start).total_seconds(),
            2
        )

        result = validated_entities["validated_entities"]

        # ==========================================
        # Classification
        # ==========================================

        start = datetime.now()
        classification = self.classifier.classify(document,result)

        processing_times["classification"] = round(
            (datetime.now() - start).total_seconds(),
            2
        )

        
        # Evidence
        start = datetime.now()
        evidence = self.evidence_engine.generate(document,result,classification)

        processing_times["evidence"] = round(
            (datetime.now() - start).total_seconds(),
            2
        )

        # Confidence
        start = datetime.now()
        confidence = self.confidence_engine.calculate(evidence,result,classification)

        processing_times["confidence"] = round(
            (datetime.now() - start).total_seconds(),
            2
        )

        # Use scraper publication date if needed
        if not result.get("dates") and clean_publication_date:
            result["dates"] = [clean_publication_date]

        # Processing Trace
        processing_times["scraping"] = round(scraping_time,2)
        processing_times["total"] = round(sum(processing_times.values()),2)

        processing_trace = {
            "status": "SUCCESS",

            "steps": [
                "Scraping",
                "Entity Extraction",
                "Validation",
                "Classification",
                "Evidence",
                "Confidence"
            ],
            "processing_time": processing_times
        }

        # Final Response
        return {

            "validated_entities": {

                "names": result.get("names", []),
                "organizations": result.get("organizations",[]),
                "locations": result.get("locations",[]),
                "dates": result.get("dates",[])
            },
            "classification": classification,
            "evidence": evidence,
            "confidence": confidence,
            "processing_trace": processing_trace,
            "rejected_entities":
                validated_entities["rejected_entities"]

        }