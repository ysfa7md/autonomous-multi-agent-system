from sre_constants import MAX_REPEAT
from typing import TypedDict


MAX_REPEAT=3
QUALITY_THRESHOLD=0.8

class ResearchState(TypedDict):
    goal: str
    tasks: list[str]
    findings: list[str]
    critique:str
    quality_score: float
    retry_count: int
    report: str
