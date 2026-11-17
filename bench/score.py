"""Quality scoring: exact match for scalars, F1 for skill lists."""

from __future__ import annotations

from typing import Any


def _norm_str(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip().lower()


def _norm_skills(skills: list[str] | None) -> set[str]:
    return {_norm_str(s) for s in (skills or []) if _norm_str(s)}


def skill_f1(predicted: list[str] | None, expected: list[str] | None) -> float:
    """Token-set F1 over skill names (case-insensitive)."""
    pred = _norm_skills(predicted)
    exp = _norm_skills(expected)
    if not pred and not exp:
        return 1.0
    if not pred or not exp:
        return 0.0
    overlap = len(pred & exp)
    precision = overlap / len(pred)
    recall = overlap / len(exp)
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def _salary_exact(pred: dict[str, Any] | None, exp: dict[str, Any] | None) -> bool:
    if pred is None and exp is None:
        return True
    if pred is None or exp is None:
        return False
    # Compare numeric bounds with small tolerance; currency/period exact (normalized).
    for key in ("min_amount", "max_amount"):
        pv, ev = pred.get(key), exp.get(key)
        if pv is None and ev is None:
            continue
        if pv is None or ev is None:
            return False
        if abs(float(pv) - float(ev)) > 1.0:
            return False
    if _norm_str(pred.get("currency")) != _norm_str(exp.get("currency")):
        return False
    if _norm_str(pred.get("period") or "unknown") != _norm_str(exp.get("period") or "unknown"):
        # If expected period is missing, don't punish unknown/None mismatch hard —
        # still require match when expected sets a period.
        if exp.get("period") is not None and pred.get("period") != exp.get("period"):
            return False
    return True


def _years_exact(pred: float | None, exp: float | None) -> bool:
    if pred is None and exp is None:
        return True
    if pred is None or exp is None:
        return False
    return abs(float(pred) - float(exp)) < 0.51


def score_posting(
    predicted: dict[str, Any] | None,
    expected: dict[str, Any],
) -> dict[str, Any]:
    """
    Return per-field scores and an overall field_accuracy in [0, 1].

    Scalars: exact (normalized string / years / salary).
    Skill lists: F1.
    If predicted is None (extract failed), all scores are 0.
    """
    fields = [
        "title",
        "company",
        "seniority",
        "location",
        "remote",
        "required_skills",
        "nice_to_have_skills",
        "years_experience",
        "salary",
    ]
    if predicted is None:
        zeros = {f: 0.0 for f in fields}
        return {**zeros, "field_accuracy": 0.0, "required_skills_f1": 0.0, "nice_to_have_skills_f1": 0.0}

    scores: dict[str, float] = {}

    for key in ("title", "company", "seniority", "location", "remote"):
        # Location/title/company: contain-or-equal soft match for small wording diffs.
        p, e = _norm_str(predicted.get(key)), _norm_str(expected.get(key))
        if not e:
            scores[key] = 1.0 if not p else 0.0
        elif p == e or (p in e) or (e in p):
            scores[key] = 1.0
        else:
            scores[key] = 0.0

    req_f1 = skill_f1(predicted.get("required_skills"), expected.get("required_skills"))
    nice_f1 = skill_f1(
        predicted.get("nice_to_have_skills"), expected.get("nice_to_have_skills")
    )
    scores["required_skills"] = req_f1
    scores["nice_to_have_skills"] = nice_f1
    scores["years_experience"] = (
        1.0 if _years_exact(predicted.get("years_experience"), expected.get("years_experience")) else 0.0
    )
    scores["salary"] = (
        1.0 if _salary_exact(predicted.get("salary"), expected.get("salary")) else 0.0
    )

    field_accuracy = sum(scores.values()) / len(fields)
    return {
        **scores,
        "required_skills_f1": req_f1,
        "nice_to_have_skills_f1": nice_f1,
        "field_accuracy": round(field_accuracy, 4),
    }
