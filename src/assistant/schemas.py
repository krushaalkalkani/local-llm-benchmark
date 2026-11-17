"""Pydantic models for structured job-posting extraction."""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field


class SalaryRange(BaseModel):
    """Optional salary band pulled from the posting."""

    min_amount: Optional[float] = Field(
        default=None,
        description="Lower bound of pay, numbers only (e.g. 120000).",
    )
    max_amount: Optional[float] = Field(
        default=None,
        description="Upper bound of pay, numbers only (e.g. 160000).",
    )
    currency: Optional[str] = Field(
        default=None,
        description="Currency code if known, e.g. USD.",
    )
    period: Optional[Literal["year", "month", "hour", "unknown"]] = Field(
        default=None,
        description="Pay period if stated.",
    )


class JobPosting(BaseModel):
    """
    Structured fields we extract from a messy job description.

    Every returned success path must validate against this model.
    """

    title: str = Field(description="Job title.")
    company: str = Field(description="Company or hiring org name.")
    seniority: Literal[
        "intern",
        "junior",
        "mid",
        "senior",
        "staff",
        "principal",
        "lead",
        "manager",
        "director",
        "unknown",
    ] = Field(description="Best-fit seniority level.")
    location: str = Field(description="City/region/country text, or 'unspecified'.")
    remote: Literal["remote", "hybrid", "onsite", "unspecified"] = Field(
        description="Work arrangement.",
    )
    required_skills: list[str] = Field(
        default_factory=list,
        description="Must-have skills mentioned in the posting.",
    )
    nice_to_have_skills: list[str] = Field(
        default_factory=list,
        description="Optional / nice-to-have skills.",
    )
    years_experience: Optional[float] = Field(
        default=None,
        description="Years of experience required, if stated.",
    )
    salary: Optional[SalaryRange] = Field(
        default=None,
        description="Salary range if present; otherwise null.",
    )


class ExtractError(BaseModel):
    """Clean failure object — never return broken JSON to the caller."""

    ok: Literal[False] = False
    error: str
    attempts: int
    raw_last_output: Optional[str] = None


class ExtractSuccess(BaseModel):
    """Validated extraction result plus validity tracking."""

    ok: Literal[True] = True
    data: JobPosting
    attempts: int
    valid_first_try: bool
    metrics: dict


ExtractResult = ExtractSuccess | ExtractError
