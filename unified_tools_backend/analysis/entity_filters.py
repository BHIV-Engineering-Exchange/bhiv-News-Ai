"""
Entity filtering rules.

Used to remove obvious false positives produced by generic NER models.

Test 2 Upgrade:
Stores rejection reasons for explainable intelligence.
"""

ENTITY_REJECTION_RULES = {
    "PERSON": {
        "html": "Technology term, not a person",
        "html5": "Technology term, not a person",
        "css": "Technology term, not a person",
        "css3": "Technology term, not a person",
        "javascript": "Programming language, not a person",
        "python": "Programming language, not a person",
        "sql": "Database language, not a person",
        "c++": "Programming language, not a person",
        "react": "Frontend framework, not a person",
        "react.js": "Frontend framework, not a person",
        "node.js": "Backend framework, not a person",
        "mongodb": "Database technology, not a person",
        "machine learning": "Academic concept, not a person",
        "chatbot": "Software concept, not a person",
        "bootstrap": "Frontend framework, not a person"
    },

    "ORG": {
        "html": "Technology term, not an organization",
        "css": "Technology term, not an organization",
        "bootstrap": "Technology term, not an organization",
        "javascript": "Programming language, not an organization",
        "machine learning": "Academic field, not an organization",
        "database systems": "Generic technical concept",
        "crud": "Software operation pattern",
        "roc": "Evaluation metric",
        "xgboost": "Machine learning algorithm",
        "random forest": "Machine learning algorithm",
        "TF-IDF":"ML algorithm",
        "random forest &": "Machine learning algorithm",
        "classifier": "Generic technical term",
        "precision recall curve": "Evaluation metric",
        "recall curve": "Evaluation metric"
    },

    "GPE": {
        "ai": "Technology domain, not a location",
        "python": "Programming language, not a location",
        "numpy": "Python library, not a location",
        "c++": "Programming language, not a location",
        "sql": "Database language, not a location",
        "roc": "Evaluation metric, not a location",
        "CSS3": "Styling language, not a location"
    }
}

GENERIC_ENTITY_TERMS = {
    "loading", "batch","json","xml","algorithm","algorithms","dataset","datasets","record",
    "records","document","documents","report","reports","unknown","sample","test","value",
    "field","column","row","cv"
}