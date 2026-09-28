import re

def extract_experience(text):
    """
    Finds mentions of years of experience in the text.
    Example matches: "3 years", "5+ years", "2-4 years of experience"
    Returns the highest number of years found, or None if nothing found.
    """
    text_lower = text.lower()

    # Pattern matches things like: "3 years", "5+ years", "3-5 years"
    pattern = r'(\d+)\s*\+?\s*(?:-\s*\d+\s*)?years?'

    matches = re.findall(pattern, text_lower)

    if not matches:
        return None

    # Convert all found numbers to integers and return the maximum
    years_found = [int(num) for num in matches]
    return max(years_found)