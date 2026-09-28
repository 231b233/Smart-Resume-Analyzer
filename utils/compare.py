def compare_skills(jd_skills, resume_skills):
    """
    Compares JD skills with resume skills
    and returns a detailed report
    """
    jd_set = set(jd_skills)
    resume_set = set(resume_skills)

    matching = jd_set & resume_set
    missing = jd_set - resume_set
    extra = resume_set - jd_set

    if len(jd_set) > 0:
        match_percentage = round((len(matching) / len(jd_set)) * 100, 2)
    else:
        match_percentage = 0

    result = {
        "match_percentage": match_percentage,
        "matching_skills": sorted(list(matching)),
        "missing_skills": sorted(list(missing)),
        "extra_skills": sorted(list(extra)),
    }

    return result


def compare_experience(jd_years, resume_years):
    """
    Compares required experience (from JD) with candidate's experience (from resume)
    """
    if jd_years is None:
        return {
            "status": "not_specified",
            "message": "No specific experience requirement found in job description."
        }

    if resume_years is None:
        return {
            "status": "unknown",
            "message": f"Job requires {jd_years}+ years experience, but couldn't detect experience in resume."
        }

    if resume_years >= jd_years:
        return {
            "status": "meets_requirement",
            "message": f"Candidate has {resume_years} years experience, meeting the required {jd_years} years."
        }
    else:
        return {
            "status": "below_requirement",
            "message": f"Candidate has {resume_years} years experience, which is below the required {jd_years} years."
        }