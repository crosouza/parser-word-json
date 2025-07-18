"""
Core parsing logic for DOCX files.
"""
import re
from docx import Document
from docx.text.paragraph import Paragraph
from parser.schema import ParsedDocument, Section, Exercise

def _is_subject_primary(p: Paragraph) -> bool:
    """Checks if a paragraph is a primary subject."""
    return p.style.name == 'Heading 3'

def _is_theory_slide(p: Paragraph) -> bool:
    """Checks if a paragraph is a theory slide."""
    return p.style.name == 'Heading 4'

def _is_exercise_intro(p: str) -> bool:
    """Checks if a paragraph is an exercise intro."""
    return bool(re.search(r'questões de exercícios', p, re.IGNORECASE))

def _is_answer(p: str) -> bool:
    """Checks if a paragraph is an answer."""
    return bool(re.search(r'gabarito|resposta', p, re.IGNORECASE))

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
            # Heuristic: Options start with A-E) or a bullet point.
            if re.match(r'^[A-Ea-e]\)', p_text) or re.match(r'^•', p_text) or p_text in ["CERTO", "ERRADO"]:
                current_exercise["options"].append(p_text)
            # Heuristic: Answer contains "Gabarito" or "Resposta".
            elif _is_answer(p_text):
                # Extract the answer from the line.
                answer = re.sub(r'gabarito|resposta', '', p_text, flags=re.IGNORECASE).strip()
                # remove : from answer
                answer = answer.replace(":", "").strip()
                current_exercise["answer"] = answer
            # Otherwise, it's part of the statement.
            else:
                current_exercise["statement"] += f"\n{p_text}"

    if current_exercise:
        if not current_exercise.get("answer"):
            warnings.append(f"Exercise {current_exercise['id']} is missing an answer.")
        exercises.append(current_exercise)

    return exercises


def _parse_sections(paragraphs: list[Paragraph], warnings: list[str]) -> list[dict]:
    sections = []
    if not paragraphs:
        return sections

    current_section = None
    state = "SEARCHING_SECTION" # SEARCHING_SECTION, IN_SECTION, IN_THEORY, IN_EXERCISE_INTRO, IN_EXERCISES
    exercise_paragraphs = []

    for p in paragraphs:
        p_text = p.text.strip()
        if not p_text:
            continue

        if _is_subject_primary(p):
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

        if state == "IN_SECTION":
            if _is_theory_slide(p):
                state = "IN_THEORY"
                current_section["theorySlides"].append(p_text)
            elif _is_exercise_intro(p_text):
                state = "IN_EXERCISE_INTRO"
                current_section["exerciseIntros"].append(p_text)
            elif not current_section.get("subjectSecondary"):
                current_section["subjectSecondary"] = p_text
        
        elif state == "IN_THEORY":
            if _is_exercise_intro(p_text):
                state = "IN_EXERCISE_INTRO"
                current_section["exerciseIntros"].append(p_text)
            elif _is_subject_primary(p):
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

    Args:
        path: The path to the .docx file.

    Returns:
        A dictionary with the parsed data.
    """
    try:
        document = Document(path)
        # Keep paragraph objects to access style information
        paragraphs = [p for p in document.paragraphs] 
    except Exception as e:
        return {"warnings": [f"Failed to read DOCX file: {e}"]}

    warnings = []
    
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

    parsed_data = {
        "courseTitle": course_title,
        "notebookTitle": notebook_title,
        "sections": sections,
        "warnings": warnings
    }

    return parsed_data
