import re


class EvidenceEngine:
    """
    Generates explainable evidence
    for extracted entities.
    """

    def generate(self,text: str,entities: dict, classification: dict = None):
        evidence_report = {}

        classification = classification or {}

        matched_keywords = classification.get("matched_keywords",[])

        paragraphs = [
            p.strip()
            for p in text.split("\n")
            if p.strip()
        ]

        for entity_group, values in entities.items():
            for entity in values:
                entity_evidence = []
                for paragraph_index, paragraph in enumerate(paragraphs,start=1):
                    sentences = re.split(
                        r"(?<=[.!?])\s+",
                        paragraph
                    )

                    for sentence in sentences:
                        if (entity.lower()in sentence.lower()):
                            classification_matches = [
                                keyword
                                for keyword in matched_keywords
                                if keyword.lower() in sentence.lower()
                            ]

                            entity_evidence.append({
                                "paragraph": paragraph_index,
                                "sentence": sentence.strip(),
                                "entity": entity,
                                "classification_keywords": classification_matches,
                                "reason": ("Entity found in article"),
                                "confidence": (
                                    1.0
                                    if classification_matches
                                    else 0.8
                                )

                            })

                if entity_evidence:
                    evidence_report[entity] = entity_evidence
        return evidence_report