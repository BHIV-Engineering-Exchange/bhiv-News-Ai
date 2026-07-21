class ClassificationEngine:

    DOMAIN_RULES = {

        "Politics": {
            "keywords": [
                "government","minister","chief minister","cm","cabinet",
                "assembly","parliament","election","mla","mp",
                "congress","bjp","brs","trs","policy","bill",
                "governor","budget","opposition","speaker",
                "president","prime minister","telangana","delhi"
            ]
        },

        "Business": {
            "keywords": [
                "stock","market","economy","gdp","investment",
                "company","startup","finance","bank","inflation",
                "profit","loss","revenue","share","industry"
            ]
        },

        "Sports": {
            "keywords": [
                "cricket","football","fifa","icc","bcci",
                "ipl","odi","test","goal","player","coach",
                "league","match","tournament","championship",
                "olympics","world cup"
            ]
        },

        "Technology": {
            "keywords": [
                "artificial intelligence","ai","machine learning",
                "deep learning","chatgpt","llm","rag",
                "google","microsoft","openai","software",
                "cybersecurity","cloud","startup","robotics"
            ]
        },

        "Health": {
            "keywords": [
                "hospital","doctor","patient","medicine",
                "medical","health","covid","virus",
                "vaccine","disease","treatment"
            ]
        },

        "Education": {
            "keywords": [
                "school","college","student","teacher",
                "university","exam","curriculum",
                "education","scholarship"
            ]
        },

        "Entertainment": {
            "keywords": [
                "actor","film","movie","cinema",
                "bollywood","hollywood","music",
                "celebrity","director","producer",
                "box office","ott"
            ]
        },

        "Crime": {
            "keywords": [
                "police","crime","murder","arrest",
                "investigation","court","judge",
                "illegal","fraud","scam","violence"
            ]
        },

        "World": {
            "keywords": [
                "united nations","usa","china","russia",
                "ukraine","iran","israel","war",
                "diplomatic","foreign","international"
            ]
        },

        "Environment": {
            "keywords": [
                "climate","forest","wildlife",
                "pollution","river","environment",
                "rainfall","flood","earthquake",
                "cyclone","weather"
            ]
        }
    }

    #v2
    def classify(self, text: str, evidence_report: dict = None):
        normalized_text = text.lower()
        scores = {}
        category_matches = {}

        for category, rule in (self.DOMAIN_RULES.items()):
            matched_keywords = []

            score = 0

            for keyword in rule["keywords"]:
                if keyword in normalized_text:
                    # Give higher weight to multi-word phrases
                    if len(keyword.split()) > 1:
                        score += 3
                    else:
                        score += 1

                    matched_keywords.append(keyword)

            scores[category] = score

            category_matches[category] = matched_keywords

        sorted_categories = sorted(
            scores.items(),
            key = lambda item: item[1],
            reverse=True
        )

        primary_category = (sorted_categories[0][0])

        secondary_category = (sorted_categories[1][0])

        top_score = (sorted_categories[0][1])

        if top_score >= 5:
            confidence_score = 0.95
        elif top_score == 4:
            confidence_score = 0.90
        elif top_score == 3:
            confidence_score = 0.80
        elif top_score == 2:
            confidence_score = 0.70
        elif top_score == 1:
            confidence_score = 0.55
        else:
            confidence_score = 0.30

        evidence_used = []

        primary_keywords = category_matches[primary_category]

        for keyword in primary_keywords:
            evidence_used.append(
                {
                    "keyword": keyword,
                    "reason":
                        f"Keyword '{keyword}' found in document"
                }
            )

        rejected_categories = {}

        for category, score in (sorted_categories[1:]):
            if score == 0:
                rejected_categories[category] = ("No supporting keywords found")
            else:
                rejected_categories[category] = (
                    f"Only {score} supporting "
                    f"keyword(s) found"
                )

        return {
            "primary_category": primary_category,
            "secondary_category": secondary_category,
            "confidence_score": confidence_score,
            "matched_keywords": category_matches[primary_category],
            "evidence_used": evidence_used,
            "rejected_categories": rejected_categories,
            "classification_explanation": (
                    f"{primary_category} selected because it contains "
                    f"{top_score} supporting keyword(s): "
                    f"{', '.join(category_matches[primary_category])}"
                )
        }