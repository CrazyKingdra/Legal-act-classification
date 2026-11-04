
from collections import Counter

# Project-specific mapping of EUROVOC Level 2 descriptors
# to our shared legal area taxonomy.

EUROVOC_TO_LEGAL_AREA = {
    # Constitutional Law
    "100163": "constitutional_law",
    "100165": "constitutional_law",
    "100166": "constitutional_law",
    "100167": "constitutional_law",
    "100184": "constitutional_law",

    # Criminal Law
    "100180": "criminal_law",

    # Civil Law
    "100179": "civil_law",

    # Public Administration
    "100169": "public_administration",
    "100174": "public_administration",

    # Taxation and Finance
    "100177": "taxation_finance",
    "100204": "taxation_finance",
    "100205": "taxation_finance",
    "100206": "taxation_finance",

    # Employment and Social Protection
    "100212": "employment_social",
    "100214": "employment_social",
    "100232": "employment_social",
    "100233": "employment_social",
    "100234": "employment_social",
    "100235": "employment_social",
    "100236": "employment_social",

    # Healthcare
    "100215": "healthcare",

    # Education and Culture
    "100213": "education_culture",
    "100217": "education_culture",
    "100218": "education_culture",
    "100219": "education_culture",

    # Economy and Business
    "100185": "economy_business",
    "100186": "economy_business",
    "100188": "economy_business",
    "100189": "economy_business",
    "100190": "economy_business",
    "100191": "economy_business",
    "100192": "economy_business",
    "100193": "economy_business",
    "100194": "economy_business",
    "100195": "economy_business",
    "100196": "economy_business",
    "100197": "economy_business",
    "100198": "economy_business",
    "100199": "economy_business",
    "100200": "economy_business",
    "100201": "economy_business",
    "100202": "economy_business",
    "100203": "economy_business",
    "100207": "economy_business",
    "100226": "economy_business",
    "100227": "economy_business",
    "100228": "economy_business",
    "100229": "economy_business",
    "100230": "economy_business",
    "100231": "economy_business",
    "100245": "economy_business",
    "100246": "economy_business",
    "100247": "economy_business",
    "100248": "economy_business",
    "100249": "economy_business",
    "100250": "economy_business",
    "100251": "economy_business",
    "100252": "economy_business",
    "100253": "economy_business",
    "100254": "economy_business",
    "100255": "economy_business",
    "100256": "economy_business",
    "100257": "economy_business",
    "100258": "economy_business",
    "100259": "economy_business",
    "100260": "economy_business",
    "100268": "economy_business",
    "100269": "economy_business",
    "100270": "economy_business",
    "100271": "economy_business",
    "100272": "economy_business",
    "100274": "economy_business",
    "100275": "economy_business",
    "100276": "economy_business",

    # Environment and Infrastructure
    "100216": "environment_infrastructure",
    "100237": "environment_infrastructure",
    "100238": "environment_infrastructure",
    "100239": "environment_infrastructure",
    "100240": "environment_infrastructure",
    "100241": "environment_infrastructure",
    "100242": "environment_infrastructure",
    "100243": "environment_infrastructure",
    "100244": "environment_infrastructure",
    "100263": "environment_infrastructure",
    "100264": "environment_infrastructure",
    "100265": "environment_infrastructure",
    "100266": "environment_infrastructure",
    "100267": "environment_infrastructure",
    "100273": "environment_infrastructure",
}


def get_majority_area(labels, label_names):
    legal_areas = []

    for label_index in labels:
        eurovoc_id = label_names[label_index]
        legal_area = EUROVOC_TO_LEGAL_AREA.get(eurovoc_id)

        if legal_area is not None:
            legal_areas.append(legal_area)

    if not legal_areas:
        return None

    area_counts = Counter(legal_areas)
    highest_count = max(area_counts.values())

    majority_areas = [
        area
        for area, count in area_counts.items()
        if count == highest_count
    ]

    if len(majority_areas) > 1:
        return None

    return majority_areas[0]
