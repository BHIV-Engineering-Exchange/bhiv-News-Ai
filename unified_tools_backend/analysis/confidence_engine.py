class ConfidenceEngine:
    """
    Generates concise and explainable confidence scores
    for News-AI intelligence.
    """

    def calculate(self, evidence_report: dict, validated_entities: dict, classification: dict):
        evidence_count = sum(len(items)
            for items in evidence_report.values()
        )

        entity_count = sum(len(items)
            for items in validated_entities.values()
        )

        classification_score = classification.get("confidence_score",0)

        # Weighted confidence
        final_score = round(
            min(
                (
                    classification_score * 60
                    + min(entity_count, 10) * 2
                    + min(evidence_count, 10) * 2
                ),
                100
            ),
            2
        )

        return {
            "score": final_score,
            "summary": (
                f"{entity_count} entities, "
                f"{evidence_count} evidence matches, "
                f"classification confidence "
                f"{classification_score}"
            )

        }