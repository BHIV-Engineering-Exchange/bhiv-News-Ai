import re
import spacy
from analysis.entity_filters import (ENTITY_REJECTION_RULES)

class EntityExtractor:
    """
    Extracts structured entities from document content.

    Supported Entities:- Names- Organizations- Locations- Dates- Emails
    - Phone Numbers - Skills - Technologies """

    SKILLS = [
        "python","java","c++","c","javascript","typescript","html","css","bootstrap","react","react.js","node.js",
        "express","mongodb","mysql","sql","git","github","tensorflow","pytorch","machine learning","deep learning",
        "artificial intelligence","data science","pandas","numpy","scikit-learn","fastapi","django","flask"
    ]

    TECH_STACK_TERMS = {

    "python","java","javascript","typescript","html","css","bootstrap","react","react.js","node.js","scikit-learn",
    "express","mongodb","mysql","sql","pandas","numpy","tensorflow","pytorch","machine learning","numpy","pandas",
    "deep learning","artificial intelligence","data science","scikit-learn","github","git","scikit",
}

    EMAIL_PATTERN = (
        r"[a-zA-Z0-9._%+-]+"
        r"@[a-zA-Z0-9.-]+"
        r"\.[a-zA-Z]{2,}"
    )

    PHONE_PATTERN = (
        r"(?:\+91[-\s]?)?"
        r"[6-9]\d{9}"
    )

    def __init__(self):
        #3
        self.nlp = self._load_nlp_model()

    @staticmethod
    def _load_nlp_model():
        for model in ("en_core_web_lg", "en_core_web_sm"):
            try:
                return spacy.load(model)
            except OSError:
                continue
        return spacy.blank("en")

    def extract(self, text: str) -> dict:
        if not text:
            return self._empty_result()

        #3 preserve original doc formating for resume header detection
        raw_text = text

        #3 create cleaned copy for NLP dont destroy og layout
        cleaned_text = re.sub(r"\s{3,}", " ", text)
        doc = self.nlp(cleaned_text)
#v2
        names = set()
        organizations = set()
        locations = set()
        dates = set()

        # Resume heuristic
        resume_name = self._extract_resume_name(raw_text)
        if resume_name:
            names.add(resume_name)

        # spaCy extraction
        for entity in doc.ents:
            value = entity.text.strip()
            
            normalized = (value.lower().strip())
            if normalized.startswith(("scikit","numpy","pandas")):
                continue
            
            # OCR merged token
            if re.search(r"[a-z][A-Z]", value):
                continue

            # Ends with dash
            if value.endswith("-"):
                continue

            # Technology terms should never
            # become ORG/GPE/PERSON
            if normalized in self.TECH_STACK_TERMS:
                continue

            # --->Early Noise Filtering
            if len(value) <= 3 and value.isupper():
                continue

            if re.search(r"\d{3,}",value):
                continue

            if re.search(r"[a-z][A-Z]", value):
                continue

            if len(value.split()) > 6:
                continue

            # Reject multiline entities
            if "\n" in value:
                continue

            # Reject excessively long entities
            if len(value.split()) > 6:
                continue

            # Reject report titles
            if value.lower().endswith(("report","chapter","contents")):
                continue
###
            if entity.label_ == "PERSON":
                value = value.strip()
                if len(value) < 3:
                    continue

                names.add(
                    value.title()
                )


            elif entity.label_ == "ORG" :
                organizations.add(value)

            elif entity.label_ == "GPE" :
                locations.add(value)

            elif entity.label_ == "DATE":
                if ( not self._looks_like_phone(value) 
                     and self._is_valid_date(value) 
                ):
                    dates.add(value)

        skills = self._extract_skills(cleaned_text)

        return {
            "names":sorted(list(names)),
            "organizations":sorted(list(organizations)),
            # "technologies":sorted(list(technologies)),
            # "skills":sorted(list(skills)),
            "locations":sorted(list(locations)),
            "dates":sorted(list(dates)),
            # "emails":sorted(list(emails)),
            # "phone_numbers":sorted(list(phone_numbers))
        }

    def _extract_resume_name(self, text: str):
        lines = text.split("\n")
        for line in lines[:10]:
            candidate = line.strip()

            # Remove email
            candidate = re.sub(r"\S+@\S+", "", candidate)

            # Remove phone
            candidate = re.sub(r"\+?\d[\d\s-]{8,}", "", candidate)

            candidate = candidate.strip()

            words = candidate.split()

            if 2 <= len(words) <= 4:
                valid_words = all(
                    word.replace(".", "").isalpha()
                    for word in words
                )

                if not valid_words:
                    continue

                if all(
                    word[0].isupper()
                    for word in words
                ):

                    return " ".join(
                        word.title()
                        for word in words
                    )

        return None

    def _extract_emails(self,text: str):
        return set(
            re.findall(self.EMAIL_PATTERN,text))

    def _extract_phone_numbers(self,text: str):
        return set(re.findall(self.PHONE_PATTERN,text))

    def _extract_skills(self,text: str):
        found_skills = set()

        normalized_text = (text.lower())

        for skill in self.SKILLS:
            pattern = (
                r"\b"
                + re.escape(skill)
                + r"\b"
            )

            if re.search(pattern,normalized_text):
                found_skills.add(skill)

        return found_skills

    def _is_valid_entity(self,entity_text: str, entity_type: str):

        candidate = (entity_text.lower().strip())
        # v2 
        rejection_rules= (ENTITY_REJECTION_RULES.get(entity_type, {}))

        return (candidate not in rejection_rules)

    def _looks_like_phone(self,value: str):

        return bool(re.fullmatch(
                r"\d{10}",
                value))
    
    def _is_valid_date(self, value: str):
        value = value.strip()
        relative_time_patterns = [
            r"\b\d+\s+minutes?\s+ago\b",
            r"\b\d+\s+hours?\s+ago\b",
            r"\b\d+\s+days?\s+ago\b",
            r"\b\d+\s+weeks?\s+ago\b",
            r"\b\d+\s+months?\s+ago\b",
            r"\b\d+\s+years?\s+ago\b",
            r"\b\d+\s+years?\s+later\b",
            r"\btoday\b",
            r"\byesterday\b",
            r"\btomorrow\b"
        ]

        for pattern in relative_time_patterns:
            if re.search(pattern, value.lower()):
                return False
            
        patterns = [
            r"\b\d{4}\b",
            r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",
            r"\b\d{1,2}\s+[A-Za-z]+\s+\d{4}\b",
            r"\b[A-Za-z]+\s+\d{4}\b",
            r"\b[A-Za-z]{3,9}\s+\d{1,2},\s+\d{4}\b",
            r"\b\d{1,2}\s+[A-Za-z]{3,9}\b",
            r"\bPublished\s*[:\-]?\s*.*",
            r"\bUpdated\s*[:\-]?\s*.*"
        ]
        for pattern in patterns:
            if re.search(pattern, value):
                return True

        return False

    def _empty_result(self):
        return {
            "names": [],
            "organizations": [],
            # "technologies": [],
            # "skills": [],
            "locations": [],
            "dates": [],
            # "emails": [],
            # "phone_numbers": []
        }