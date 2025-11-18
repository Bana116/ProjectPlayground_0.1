from backend.models import db, Designer, Founder, Match


# -------------------------------------------------
# Helper: Check if this designer already matched this founder
# -------------------------------------------------
def has_matched_before(founder_id, designer_id):
    return Match.query.filter_by(
        founder_id=founder_id,
        designer_id=designer_id
    ).first() is not None


# -------------------------------------------------
# Simple scoring system (upgrade this anytime)
# -------------------------------------------------
def score_match(founder, designer):
    score = 0

    # Basic simple keyword match (MVP-friendly)
    if founder.needs and designer.skills:
        needs_list = founder.needs.lower().split(",")
        skills_list = designer.skills.lower().split(",")

        for need in needs_list:
            if need.strip() in [s.strip() for s in skills_list]:
                score += 10

    # More experience = slightly better
    if designer.experience:
        score += len(designer.experience) * 0.2

    return score


# -------------------------------------------------
# Find designers for a founder (match pool)
# -------------------------------------------------
def find_matches_for_founder(founder, limit=3):
    """
    Returns up to 3 best designers for this founder
    ignoring designers they've already matched with.
    """

    designers = Designer.query.all()
    if not designers:
        return []

    scored_designers = []

    for designer in designers:
        # skip if they've matched before (no duplicate matches)
        if has_matched_before(founder.id, designer.id):
            continue

        match_score = score_match(founder, designer)
        scored_designers.append((designer, match_score))

    # sort by score, highest first
    scored_designers.sort(key=lambda x: x[1], reverse=True)

    # return only designer objects
    best_designers = [d[0] for d in scored_designers[:limit]]

    return best_designers


# -------------------------------------------------
# Pick a single designer (if you want single match mode)
# -------------------------------------------------
def find_single_best_match(founder):
    designers = find_matches_for_founder(founder, limit=1)

    if designers:
        return designers[0]
    return None
