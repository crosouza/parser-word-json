"""
JSON Schema for the parsed document.
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class Exercise(BaseModel):
    """Represents a single exercise."""
    id: int
    statement: str
    options: List[str]
    answer: str


class Section(BaseModel):
    """Represents a section of the document."""
    subjectPrimary: str = Field(..., alias="subjectPrimary")
    subjectSecondary: Optional[str] = Field(None, alias="subjectSecondary")
    theorySlides: List[str] = Field(default_factory=list, alias="theorySlides")
    exerciseIntros: List[str] = Field(default_factory=list, alias="exerciseIntros")
    exercises: List[Exercise] = Field(default_factory=list)


class ParsedDocument(BaseModel):
    """Represents the entire parsed document."""
    courseTitle: str = Field(..., alias="courseTitle")
    notebookTitle: str = Field(..., alias="notebookTitle")
    sections: List[Section] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)

