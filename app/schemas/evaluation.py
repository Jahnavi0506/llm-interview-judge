from pydantic import BaseModel, Field
from typing import List, Dict, Literal


class EvaluationOutput(BaseModel):
    """
    Schema for the evaluation result returned by Gemini.
    Every evaluation must match this exact structure.
    """
    score: float = Field(ge=0, le=10, description="Score between 0 and 10")
    strengths: List[str] = Field(description="What the candidate got right")
    weaknesses: List[str] = Field(description="What was wrong or imprecise")
    missing_concepts: List[str] = Field(description="Key concepts not mentioned")
    concept_coverage: Dict[str, Literal["covered", "partial", "missing"]] = Field(
        description="Coverage status of each key concept"
    )
    improved_answer: str = Field(description="A model answer a strong candidate would give")
    interviewer_note: str = Field(description="One line summary of candidate performance")