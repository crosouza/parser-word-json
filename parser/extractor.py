"""
Core parsing logic for DOCX files.
"""
import re
from docx import Document
from docx.text.paragraph import Paragraph
from parser.schema import ParsedDocument, Section, Exercise
from parser.utils import (
    is_subject_primary,
    is_theory_slide,
    is_exercise_intro,
    is_answer,
    is_option,
)

def _parse_exercises(paragraphs: list[str], warnings: list[str]) -> list[dict]:
    exercises = []
    if not paragraphs:
        return exercises

    current_exercise = None
    exercise_counter = 1

    for p_text in paragraphs:
        # Heuristic: Exercise starts with a number followed by a parenthesis or a dot.
        if re.match(r'^\d+[\.\)]', p_text):
            if current_exercise:
                if not current_exercise.get("options"):
                    warnings.append(f"Exercise {current_exercise['id']} is missing options.")
                if not current_exercise.get("answer"):
                    warnings.append(f"Exercise {current_exercise['id']} is missing an answer.")
                exercises.append(current_exercise)
            
            current_exercise = {
                "id": exercise_counter,
                "statement": p_text,
                "options": [],
                "answer": None
            }
            exercise_counter += 1
            continue

        if current_exercise:
            if is_option(p_text):
                current_exercise["options"].append(p_text)
            elif is_answer(p_text):
                answer = re.sub(r'gabarito|resposta|alternativa correta|correto', '', p_text, flags=re.IGNORECASE).strip()
                answer = answer.replace(":", "").strip()
                current_exercise["answer"] = answer
            else:
                current_exercise["statement"] += f"\n{p_text}"

    if current_exercise:
        if not current_exercise.get("options"):
            warnings.append(f"Exercise {current_exercise['id']} is missing options.")
        if not current_exercise.get("answer"):
            warnings.append(f"Exercise {current_exercise['id']} is missing an answer.")
        exercises.append(current_exercise)

    return exercises


def _parse_sections(paragraphs: list[Paragraph], warnings: list[str]) -> list[dict]:
    sections = []
    if not paragraphs:
        return sections

    current_section = None
    state = "SEARCHING_SECTION"
    exercise_paragraphs = []

    for p in paragraphs:
        p_text = p.text.strip()
        if not p_text:
            continue

        if is_subject_primary(p):
            if current_section:
                if exercise_paragraphs:
                    current_section["exercises"] = _parse_exercises(exercise_paragraphs, warnings)
                    exercise_paragraphs = []
                sections.append(current_section)

            current_section = {
                "subjectPrimary": p_text,
                "subjectSecondary": None,
                "theorySlides": [],
                "exerciseIntros": [],
                "exercises": []
            }
            state = "IN_SECTION"
            continue

        if not current_section:
            continue

        if state == "IN_SECTION":
            if is_theory_slide(p):
                state = "IN_THEORY"
                current_section["theorySlides"].append(p_text)
            elif is_exercise_intro(p_text):
                state = "IN_EXERCISE_INTRO"
                current_section["exerciseIntros"].append(p_text)
            elif not current_section.get("subjectSecondary"):
                current_section["subjectSecondary"] = p_text
        
        elif state == "IN_THEORY":
            if is_exercise_intro(p_text):
                state = "IN_EXERCISE_INTRO"
                current_section["exerciseIntros"].append(p_text)
            elif is_subject_primary(p):
                if current_section:
                    sections.append(current_section)
                current_section = {
                    "subjectPrimary": p_text,
                    "subjectSecondary": None,
                    "theorySlides": [],
                    "exerciseIntros": [],
                    "exercises": []
                }
                state = "IN_SECTION"
            else:
                current_section["theorySlides"].append(p_text)

        elif state == "IN_EXERCISE_INTRO":
            state = "IN_EXERCISES"
            exercise_paragraphs.append(p_text)

        elif state == "IN_EXERCISES":
            exercise_paragraphs.append(p_text)

    if current_section:
        if exercise_paragraphs:
            current_section["exercises"] = _parse_exercises(exercise_paragraphs, warnings)
        sections.append(current_section)
        
    return sections


def parse_docx(path: str) -> dict:
    """
    Parses a .docx file and returns a dictionary conforming to the schema.
    """
    try:
        document = Document(path)
        paragraphs = list(document.paragraphs)
    except Exception as e:
        return {"warnings": [f"Failed to read DOCX file: {e}"]}

    warnings = []
    
    # Find course and notebook titles
    course_title = ""
    if paragraphs:
        p = paragraphs.pop(0)
        course_title = p.text.strip()
        if p.style.name != 'Heading 1' and not course_title.isupper():
            warnings.append(f"Course title might be incorrect: '{course_title}' is not Heading 1 or all caps.")

    notebook_title = ""
    if paragraphs:
        p = paragraphs.pop(0)
        notebook_title = p.text.strip()
        if p.style.name != 'Heading 2' and not notebook_title.isupper():
            warnings.append(f"Notebook title might be incorrect: '{notebook_title}' is not Heading 2 or all caps.")

    sections = _parse_sections(paragraphs, warnings)

    return {
        "courseTitle": course_title,
        "notebookTitle": notebook_title,
        "sections": sections,
        "warnings": warnings
    }
