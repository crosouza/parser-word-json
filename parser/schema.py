"""
JSON Schema for the parsed document.
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class TheorySlide(BaseModel):
    """Represents a single theory slide."""
    title: str
    content: str


class ExerciseQuestion(BaseModel):
    """Represents a single question within an exercise."""
    question: str
    answer: str


class Exercise(BaseModel):
    """Represents an exercise block with a statement and questions."""
    statement: str
    questions: List[ExerciseQuestion]


class Subject(BaseModel):
    """Represents a subject with theory and exercises."""
    subjectName: str
    theorySlides: List[TheorySlide] = Field(default_factory=list)
    exercises: List[Exercise] = Field(default_factory=list)


class ContestQuestion(BaseModel):
    """Represents a single contest question."""
    id: int
    statement: str
    text: Optional[str] = None
    source: Optional[str] = None
    options: List[str]
    answer: str


class ParsedDocument(BaseModel):
    """Represents the entire parsed document."""
    courseTitle: str = Field(..., alias="courseTitle")
    notebookTitle: str = Field(..., alias="notebookTitle")
    programmaticContent: str = Field(..., alias="programmaticContent")
    subjects: List[Subject] = Field(default_factory=list)
    contestQuestions: List[ContestQuestion] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)