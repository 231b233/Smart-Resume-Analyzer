from data.skills_list import COMMON_SKILLS, SKILL_SYNONYMS

def normalize_text(text):
    """
    Replaces known synonyms/abbreviations in the text
    with their standard skill name
    """
    text_lower = text.lower()
    for synonym, standard_name in SKILL_SYNONYMS.items():
        text_lower = text_lower.replace(synonym, standard_name)
    return text_lower

def extract_skills(text):
    """
    Finds and returns skills from the given text
    that match the COMMON_SKILLS list (after normalizing synonyms)
    """
    text_lower = normalize_text(text)
    found_skills = []

    for skill in COMMON_SKILLS:
        if skill.lower() in text_lower:
            found_skills.append(skill)

    return found_skills