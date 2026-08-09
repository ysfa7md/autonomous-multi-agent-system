"""
agent/models.py
Pydantic schema for the validated final report. The Reporting node must
produce a validated object, not a raw string dump — this is that object.
"""
from pydantic import BaseModel, Field


class FinalReport(BaseModel):
    goal: str
    quality_score: float = Field(ge=0.0, le=1.0)
    retries_used: int = Field(ge=0)
    below_threshold: bool
    findings: list[str]
    critique: str = ""

    def to_markdown(self) -> str:
        findings_md = "\n".join(f"- {f}" for f in self.findings) or "- (none)"
        header = "# Research Report\n\n"
        if self.below_threshold:
            header += (
                "> ⚠️ **Accepted below threshold** — retry cap reached "
                f"(score {round(self.quality_score, 2)}).\n\n"
            )
        return (
            f"{header}"
            f"**Goal:** {self.goal}\n\n"
            f"**Quality score:** {round(self.quality_score, 2)}\n\n"
            f"**Retries used:** {self.retries_used}\n\n"
            f"## Findings\n{findings_md}\n\n"
            f"## Critique\n{self.critique or 'None'}\n"
        )
